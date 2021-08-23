import gym
from gym import error, spaces, utils
from gym.utils import seeding

import os
import pybullet as p
import pybullet_data
import math
import numpy as np
import random
from pprint import pprint
import matplotlib.pyplot as plt

from .pdControllerExplicit import PDControllerExplicit
#from .pdControllerStable import PDControllerStable

TIME_STEP=1.0/240
#TIME_STEP=1.0/2000

MAX_TORQUE=100

def q_mul(quaternion1, quaternion0):
    x0, y0, z0, w0 = quaternion0
    x1, y1, z1, w1 = quaternion1
    return np.array([
      x1 * w0 + y1 * z0 - z1 * y0 + w1 * x0,
      -x1 * z0 + y1 * w0 + z1 * x0 + w1 * y0,
      x1 * y0 - y1 * x0 + z1 * w0 + w1 * z0,
      -x1 * x0 - y1 * y0 - z1 * z0 + w1 * w0
    ], dtype=np.float64)

def q_to_eu(q):
    x=q[0]
    y=q[1]
    z=q[2]
    w=q[3]
    ysqr = y * y

    t0 = +2.0 * (w * x + y * z)
    t1 = +1.0 - 2.0 * (x * x + ysqr)
    X = math.degrees(math.atan2(t0, t1))

    t2 = +2.0 * (w * y - z * x)
    t2 = +1.0 if t2 > +1.0 else t2
    t2 = -1.0 if t2 < -1.0 else t2
    Y = math.degrees(math.asin(t2))

    t3 = +2.0 * (w * z + x * y)
    t4 = +1.0 - 2.0 * (ysqr + z * z)
    Z = math.degrees(math.atan2(t3, t4))

    return [X, Y, Z]

class NFEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self,show_gui=False,fall_rew=-10,motion_rew=0,const_rew=2,height_rew=0,rand_force=[0,0,0],rand_force_freq=0,mp4_path=None,foot_friction_lat=1,foot_friction_spin=1,pitch_rew=-1,roll_rew=-1,distance_rew=0,max_distance=0,power_rew=-0.1,min_height=0.5,max_pitch=0.9,max_roll=0,target_height=1.7,speed_x_rew=-0.1,speed_y_rew=-0.1,speed_z_rew=0,speed_pitch_rew=0,speed_roll_rew=0,speed_yaw_rew=0,max_steps=5000,debug=False,base_mass=4,min_actions=[-1]*4,max_actions=[1]*4,target_speed_x=0,target_speed_y=0,action_sim_steps=int((1.0/TIME_STEP)/40),rand_action_delay=0,max_torque=MAX_TORQUE,kp_max=200,kd_max=3,max_episode_len=400,rand_max_torque=[20,100],rand_friction=[0.5,3],min_z=0.1,max_z=0.8,max_x=0.8,max_y=0.8,rand_pos=0):
        self.step_counter = 0
        if show_gui:
            mode=p.GUI
        else:
            mode=p.DIRECT
        options=""
        if mp4_path:
            options+="--width=1024 --height=768 --mp4=\""+mp4_path+"\" --mp4fps=%s"%(240/action_sim_steps,)
        p.connect(mode, options=options)
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setTimeStep(TIME_STEP)
        self.observation_space = spaces.Box(np.array([-1]*20), np.array([1]*20))
        self.min_actions=min_actions
        self.max_actions=max_actions
        self.action_space = spaces.Box(np.array(self.min_actions), np.array(self.max_actions))
        self.prev_pos=None
        self.fall_rew=fall_rew
        self.motion_rew=motion_rew
        self.const_rew=const_rew
        self.height_rew=height_rew
        self.pitch_rew=pitch_rew
        self.roll_rew=roll_rew
        self.distance_rew=distance_rew
        self.power_rew=power_rew
        self.max_distance=max_distance
        self.rand_force=rand_force
        self.foot_friction_lat=foot_friction_lat
        self.foot_friction_spin=foot_friction_spin
        self.rand_friction=rand_friction
        self.min_height=min_height
        self.max_pitch=max_pitch
        self.max_roll=max_roll
        self.target_height=target_height
        self.rand_force_freq=rand_force_freq
        self.speed_x_rew=speed_x_rew
        self.speed_y_rew=speed_y_rew
        self.speed_z_rew=speed_z_rew
        self.speed_pitch_rew=speed_pitch_rew
        self.speed_roll_rew=speed_roll_rew
        self.speed_yaw_rew=speed_yaw_rew
        self.max_steps=max_steps
        self.debug=debug
        self.base_mass=base_mass
        self.target_speed_x=target_speed_x
        self.target_speed_y=target_speed_y
        self.action_sim_steps=action_sim_steps
        self.rand_action_delay=rand_action_delay
        self.exPD = PDControllerExplicit(p)
        #self.sPD = PDControllerStable(p)
        self.max_torque=max_torque
        self.rand_max_torque=rand_max_torque
        self.kp_max=kp_max
        self.kd_max=kd_max
        self.max_episode_len=max_episode_len
        self.min_z=min_z
        self.max_z=max_z
        self.max_x=max_x
        self.max_y=max_y
        self.max_pitch=max_pitch
        self.rand_pos=rand_pos

    def reset(self):
        open("orient.txt","w").write("")
        open("angvel.txt","w").write("")
        self.step_counter = 0
        p.resetSimulation()
        p.setGravity(0,0,-10)
        self.plane_id = p.loadURDF("plane.urdf")
        #self.wall1_id = p.loadURDF("plane.urdf",[-0.7,0,0],p.getQuaternionFromEuler([0,math.pi/2,0]))
        #self.wall2_id = p.loadURDF("plane.urdf",[0.7,0,0],p.getQuaternionFromEuler([0,-math.pi/2,0]))
        cubeStartPos = [0,0,0.3]
        #cubeStartPos = [0,0,2]
        cubeStartOrientation = p.getQuaternionFromEuler([0,0,0])
        #cubeStartOrientation = p.getQuaternionFromEuler([0,0,math.pi/2])
        #cubeStartOrientation = p.getQuaternionFromEuler([math.pi/6,0,0])
        #cubeStartOrientation = [1,0,0,0]
        try:
            #self.bot_id = p.loadURDF("/Users/davidjanssens/stuff/bot/urdf/z1bot.urdf", cubeStartPos, cubeStartOrientation)
            self.bot_id = p.loadURDF("/Users/davidjanssens/stuff/bot/urdf/z2bot.urdf", cubeStartPos, cubeStartOrientation)
        except:
            self.bot_id = p.loadURDF("/content/drive/My Drive/bot/z2bot.urdf", cubeStartPos, cubeStartOrientation)

        self.joints={}
        self.joint_limits={}
        n=p.getNumJoints(self.bot_id)
        for i in range(n):
            res=p.getJointInfo(self.bot_id,i)
            #print("joint #%d: %s"%(i,res))
            self.joints[res[1].decode()]=i
            self.joint_limits[res[1].decode()]=(res[8],res[9])

        maxForce = 0
        mode = p.VELOCITY_CONTROL
        for n,i in self.joints.items():
            p.setJointMotorControl2(self.bot_id, i, controlMode=mode, force=maxForce)

        """
        p.changeDynamics(self.bot_id, -1, mass=self.base_mass)
        if self.debug:
            res=p.getDynamicsInfo(self.bot_id, -1)
            print("base dynamics:",res)
            for i in range(8):
                res=p.getDynamicsInfo(self.bot_id, i)
                print("link #%s dynamics:"%i,res)
        """

        p.createConstraint(self.bot_id, self.joints["rods_to_rod_l"], self.bot_id, self.joints["knee_to_lleg_l"], jointType=p.JOINT_POINT2POINT,jointAxis=[0,0,0],parentFramePosition=[0,0,-0.217],childFramePosition=[-0.11+0.005,0,0.026])
        p.createConstraint(self.bot_id, self.joints["rods_to_rod_r"], self.bot_id, self.joints["knee_to_lleg_r"], jointType=p.JOINT_POINT2POINT,jointAxis=[0,0,0],parentFramePosition=[0,0,-0.217],childFramePosition=[-0.11+0.005,0,0.026])

        """
        lim=self.joint_limits["umot_to_mbar_l"]
        #p.resetJointState(self.bot_id, self.joints["umot_to_mbar_l"], lim[0])
        p.setJointMotorControl2(self.bot_id, self.joints["umot_to_mbar_l"], controlMode=p.POSITION_CONTROL, targetPosition=lim[0]*0.5)
        lim=self.joint_limits["umot_to_mbar_r"]
        #p.resetJointState(self.bot_id, self.joints["umot_to_mbar_r"], lim[0])
        p.setJointMotorControl2(self.bot_id, self.joints["umot_to_mbar_r"], controlMode=p.POSITION_CONTROL, targetPosition=lim[0]*0.5)
        lim=self.joint_limits["lmot_to_uleg_l"]
        #p.resetJointState(self.bot_id, self.joints["lmot_to_uleg_l"], lim[1])
        p.setJointMotorControl2(self.bot_id, self.joints["lmot_to_uleg_l"], controlMode=p.POSITION_CONTROL, targetPosition=lim[1]*0.5)
        lim=self.joint_limits["lmot_to_uleg_r"]
        #p.resetJointState(self.bot_id, self.joints["lmot_to_uleg_r"], lim[1])
        p.setJointMotorControl2(self.bot_id, self.joints["lmot_to_uleg_r"], controlMode=p.POSITION_CONTROL, targetPosition=lim[1]*0.5)
        """

        """
        p.resetBasePositionAndOrientation(self.bot_id, [0,0,1], [0,0,0,1])
        p.resetBaseVelocity(self.bot_id, [0,0,0], [0,0,0])

        taus=[0]*4
        p.setJointMotorControl2(self.bot_id, self.joints["umot_to_mbar_l"], controlMode=p.TORQUE_CONTROL, force=taus[0])
        p.setJointMotorControl2(self.bot_id, self.joints["umot_to_mbar_r"], controlMode=p.TORQUE_CONTROL, force=taus[1])
        p.setJointMotorControl2(self.bot_id, self.joints["lmot_to_uleg_l"], controlMode=p.TORQUE_CONTROL, force=taus[2])
        p.setJointMotorControl2(self.bot_id, self.joints["lmot_to_uleg_r"], controlMode=p.TORQUE_CONTROL, force=taus[3])
        for i in range(100):
            p.stepSimulation()
        """

        #p.enableJointForceTorqueSensor(self.bot_id, self.joints["lleg_to_foot_l"], 1)
        #p.enableJointForceTorqueSensor(self.bot_id, self.joints["lleg_to_foot_r"], 1)

        action=[
            1,0,0,
            1,0,0,
            -1,0,0,
            -1,0,0,
            0,0,0,
            0,0,0,
        ]
        pos=[None]*6
        kp=[None]*6
        kd=[None]*6

        lim=self.joint_limits["umot_to_mbar_l"]
        pos[0]=min(max(-action[0]*max(-lim[0],lim[1]),lim[0]),lim[1])
        kp[0]=(1+action[1])*self.kp_max/2
        kd[0]=(1+action[2])*self.kd_max/2
        #print("set umot_to_mbar_l pos=%s kp=%s kd=%s"%(pos[0],kp[0],kd[0]))

        lim=self.joint_limits["umot_to_mbar_r"]
        pos[1]=min(max(-action[3]*max(-lim[0],lim[1]),lim[0]),lim[1])
        kp[1]=(1+action[4])*self.kp_max/2
        kd[1]=(1+action[5])*self.kd_max/2
        #print("set umot_to_mbar_r pos=%s kp=%s kd=%s"%(pos[1],kp[1],kd[1]))

        lim=self.joint_limits["lmot_to_uleg_l"]
        pos[2]=min(max(-action[6]*max(-lim[0],lim[1]),lim[0]),lim[1])
        kp[2]=(1+action[7])*self.kp_max/2
        kd[2]=(1+action[8])*self.kd_max/2
        #print("set lmot_to_uleg_l pos=%s kp=%s kd=%s"%(pos[2],kp[2],kd[2]))

        lim=self.joint_limits["lmot_to_uleg_r"]
        pos[3]=min(max(-action[9]*max(-lim[0],lim[1]),lim[0]),lim[1])
        kp[3]=(1+action[10])*self.kp_max/2
        kd[3]=(1+action[11])*self.kd_max/2
        #print("set lmot_to_uleg_r pos=%s kp=%s kd=%s"%(pos[3],kp[3],kd[3]))

        lim=self.joint_limits["hmot_to_hip_l"]
        pos[4]=min(max(action[12]*max(-lim[0],lim[1]),lim[0]),lim[1])
        kp[4]=(1+action[13])*self.kp_max/2
        kd[4]=(1+action[14])*self.kd_max/2
        #print("set hmot_to_hip_l pos=%s kp=%s kd=%s"%(pos[4],kp[4],kd[4]))

        lim=self.joint_limits["hmot_to_hip_r"]
        pos[5]=min(max(-action[15]*max(-lim[0],lim[1]),lim[0]),lim[1])
        kp[5]=(1+action[16])*self.kp_max/2
        kd[5]=(1+action[17])*self.kd_max/2
        #print("set hmot_to_hip_r pos=%s kp=%s kd=%s"%(pos[4],kp[4],kd[4]))

        for i in range(30):
            #print("reset i=%s"%i)
            for j in range(self.action_sim_steps):
                joints=[
                    self.joints["umot_to_mbar_l"],
                    self.joints["umot_to_mbar_r"],
                    self.joints["lmot_to_uleg_l"],
                    self.joints["lmot_to_uleg_r"],
                    self.joints["hmot_to_hip_l"],
                    self.joints["hmot_to_hip_r"],
                ]
                taus = self.exPD.computePD(self.bot_id, joints, pos, [0]*6, kp, kd, [self.max_torque]*6, TIME_STEP)
                #print("taus",taus)
                if i<10:
                    p.resetBaseVelocity(self.bot_id, [0,0,0], [0,0,0])

                p.setJointMotorControl2(self.bot_id, self.joints["umot_to_mbar_l"], controlMode=p.TORQUE_CONTROL, force=taus[0])
                p.setJointMotorControl2(self.bot_id, self.joints["umot_to_mbar_r"], controlMode=p.TORQUE_CONTROL, force=taus[1])
                p.setJointMotorControl2(self.bot_id, self.joints["lmot_to_uleg_l"], controlMode=p.TORQUE_CONTROL, force=taus[2])
                p.setJointMotorControl2(self.bot_id, self.joints["lmot_to_uleg_r"], controlMode=p.TORQUE_CONTROL, force=taus[3])
                p.setJointMotorControl2(self.bot_id, self.joints["hmot_to_hip_l"], controlMode=p.TORQUE_CONTROL, force=taus[4])
                p.setJointMotorControl2(self.bot_id, self.joints["hmot_to_hip_r"], controlMode=p.TORQUE_CONTROL, force=taus[5])

                p.stepSimulation()

        if self.rand_friction:
            self.foot_friction_lat=random.uniform(self.rand_friction[0],self.rand_friction[1])
            self.foot_friction_spin=self.foot_friction_lat # XXX
            if self.debug:
                print("friction:",self.foot_friction_lat)
        p.changeDynamics(self.bot_id, self.joints["lleg_to_foot_l"], lateralFriction=self.foot_friction_lat, spinningFriction=self.foot_friction_spin)
        p.changeDynamics(self.bot_id, self.joints["lleg_to_foot_r"], lateralFriction=self.foot_friction_lat, spinningFriction=self.foot_friction_spin)

        #p.enableJointForceTorqueSensor(self.bot_id, self.joints["umot_to_mbar_l"]) # XXX
        self.all_obs=[]
        self.all_torques=[]
        self.all_actions=[]
        self.all_rews=[]

        obs=self.get_obs()
        self.observation = obs 

        self.all_obs.append(obs)

        self.done=False
        if self.rand_max_torque:
            self.max_torque=random.uniform(self.rand_max_torque[0],self.rand_max_torque[1])
            if self.debug:
                print("max_torque",self.max_torque)

        return np.array(self.observation).astype(np.float32)

    def get_obs(self):
        res=p.getBasePositionAndOrientation(self.bot_id)
        pos=res[0]
        q=res[1]
        q_=[-q[0],-q[1],-q[2],q[3]]
        rot=p.getEulerFromQuaternion(q)
        #pitch=rot[0]
        #roll=rot[1]
        yaw=rot[2]
        x=q_mul(q_mul(q,[1,0,0,0]),q_) # b->w
        y=q_mul(q_mul(q,[0,1,0,0]),q_) # b->w
        z=q_mul(q_mul(q,[0,0,1,0]),q_) # b->w
        #res=q_to_eu(q)
        #roll=res[0]
        #pitch=res[1]
        #yaw=res[2]
        pitch=x[2]
        roll=y[2]
        if z[2]<0:
            pitch=1 if x[2]>0 else -1 # XXX

        rot_around_z = np.array([[np.cos(-yaw),-np.sin(-yaw), 0], [np.sin(-yaw), np.cos(-yaw), 0], [0, 0, 1]])

        res=p.getBaseVelocity(self.bot_id)
        lv_w=list(res[0])+[0]
        av_w=list(res[1])+[0]
        if self.debug:
            print("av_w",av_w)
        lv_b=q_mul(q_mul(q_,lv_w),q) # w->b
        av_b=q_mul(q_mul(q_,av_w),q) # w->b
        if self.debug:
            print("av_b",av_b)
        #lin_vel=np.dot(rot_around_z,res[0]).tolist()
        #ang_vel=np.dot(rot_around_z,res[1]).tolist()
        lin_vel=[lv_b[0],lv_b[1],lv_b[2]] # XXX
        ang_vel=[-av_b[1],av_b[0],av_b[2]] # XXX

        obs=[]
        obs+=[pitch,roll] # orient (2)
        obs+=[ang_vel[0]/math.pi,ang_vel[1]/math.pi,ang_vel[2]/math.pi] # ang vel (3)
        obs+=lin_vel # lin vel (3)
        s=p.getJointState(self.bot_id, self.joints["umot_to_mbar_l"])
        obs.append(s[0]/math.pi) # pos
        obs.append(s[1]/math.pi) # vel
        s=p.getJointState(self.bot_id, self.joints["umot_to_mbar_r"])
        obs.append(s[0]/math.pi) # pos
        obs.append(s[1]/math.pi) # vel
        s=p.getJointState(self.bot_id, self.joints["lmot_to_uleg_l"])
        obs.append(s[0]/math.pi) # pos
        obs.append(s[1]/math.pi) # vel
        s=p.getJointState(self.bot_id, self.joints["lmot_to_uleg_r"])
        obs.append(s[0]/math.pi) # pos
        obs.append(s[1]/math.pi) # vel
        s=p.getJointState(self.bot_id, self.joints["hmot_to_hip_l"])
        obs.append(s[0]/math.pi) # pos
        obs.append(s[1]/math.pi) # vel
        s=p.getJointState(self.bot_id, self.joints["hmot_to_hip_r"])
        obs.append(s[0]/math.pi) # pos
        obs.append(s[1]/math.pi) # vel

        if self.debug:
            print("-"*80)
            print("obs:")
            print("orient: p=%s r=%s"%(obs[0],obs[1]))
            print("ang_vel: p=%s r=%s y=%s"%(obs[2],obs[3],obs[4]))
            print("lin_vel: x=%s y=%s z=%s"%(obs[5],obs[6],obs[7]))
            print("umot_to_mbar_l: pos=%s vel=%s"%(obs[8],obs[9]))
            print("umot_to_mbar_l: pos=%s vel=%s"%(obs[10],obs[11]))
            print("lmot_to_uleg_l: pos=%s vel=%s"%(obs[12],obs[13]))
            print("lmot_to_uleg_r: pos=%s vel=%s"%(obs[14],obs[15]))
            print("hmot_to_hip_l: pos=%s vel=%s"%(obs[16],obs[17]))
            print("hmot_to_hip_r: pos=%s vel=%s"%(obs[18],obs[19]))
        return obs

    def step(self, action):
        action=np.array(action)
        action=np.maximum(action,self.min_actions)
        action=np.minimum(action,self.max_actions)

        apply_force=random.random()<self.rand_force_freq
        if apply_force:
            r=random.uniform(-1,1)
            f=np.array(self.rand_force)*r
            if self.debug:
                print("*"*80)
                print("*"*80)
                print("*"*80)
                print("apply rand force",f)
            p.applyExternalForce(self.bot_id,-1,f,[0,0,0],p.WORLD_FRAME)

        delays=[]
        for i in range(6):
            delays.append(random.randint(0,self.rand_action_delay))
        #if self.debug:
            #print("delays:",delays)

        pos=[None]*6

        lim=self.joint_limits["umot_to_mbar_l"]
        pos[0]=min(max(-action[0]*max(-lim[0],lim[1]),lim[0]),lim[1])
        if self.rand_pos:
            pos[0]*random.uniform(1,1+self.rand_pos)

        lim=self.joint_limits["umot_to_mbar_r"]
        pos[1]=min(max(-action[1]*max(-lim[0],lim[1]),lim[0]),lim[1])
        if self.rand_pos:
            pos[1]*random.uniform(1,1+self.rand_pos)

        lim=self.joint_limits["lmot_to_uleg_l"]
        pos[2]=min(max(-action[2]*max(-lim[0],lim[1]),lim[0]),lim[1])
        if self.rand_pos:
            pos[2]*random.uniform(1,1+self.rand_pos)

        lim=self.joint_limits["lmot_to_uleg_r"]
        pos[3]=min(max(-action[3]*max(-lim[0],lim[1]),lim[0]),lim[1])
        if self.rand_pos:
            pos[3]*random.uniform(1,1+self.rand_pos)

        pos[4]=0
        pos[5]=0
        taus=[0]*6

        p.setJointMotorControl2(self.bot_id, self.joints["umot_to_mbar_l"], controlMode=p.POSITION_CONTROL, targetPosition=pos[0], force=self.max_torque)
        p.setJointMotorControl2(self.bot_id, self.joints["umot_to_mbar_r"], controlMode=p.POSITION_CONTROL, targetPosition=pos[1], force=self.max_torque)
        p.setJointMotorControl2(self.bot_id, self.joints["lmot_to_uleg_l"], controlMode=p.POSITION_CONTROL, targetPosition=pos[2], force=self.max_torque)
        p.setJointMotorControl2(self.bot_id, self.joints["lmot_to_uleg_r"], controlMode=p.POSITION_CONTROL, targetPosition=pos[3], force=self.max_torque)
        p.setJointMotorControl2(self.bot_id, self.joints["hmot_to_hip_l"], controlMode=p.POSITION_CONTROL, targetPosition=pos[4], force=self.max_torque)
        p.setJointMotorControl2(self.bot_id, self.joints["hmot_to_hip_r"], controlMode=p.POSITION_CONTROL, targetPosition=pos[5], force=self.max_torque)

        for j in range(self.action_sim_steps):
            p.stepSimulation()

        obs=self.get_obs()
        self.observation = obs 
        self.all_obs.append(obs)
        self.all_torques.append(taus)

        res=p.getBasePositionAndOrientation(self.bot_id)
        pos=res[0]
        height=pos[2]
        if self.debug:
            print("pos",pos)
        q=res[1]
        rot=p.getEulerFromQuaternion(q)
        yaw=rot[2]

        """
        res=p.getJointState(self.bot_id,self.joints["lleg_to_foot_l"])
        l_forces=res[2]
        l_force=np.linalg.norm(l_forces[:3])
        if self.debug:
            print("left foot force:",l_force,l_forces)
        res=p.getJointState(self.bot_id,self.joints["lleg_to_foot_r"])
        r_forces=res[2]
        r_force=np.linalg.norm(r_forces[:3])
        if self.debug:
            #print("right foot forces:",r_forces)
            print("right foot force:",r_force,r_forces)
        """

        res=p.getLinkState(self.bot_id,self.joints["lleg_to_foot_l"])
        lfoot_z=res[0][2]
        res=p.getLinkState(self.bot_id,self.joints["lleg_to_foot_r"])
        rfoot_z=res[0][2]
        res=p.getLinkState(self.bot_id,self.joints["uleg_to_knee_l"])
        lknee_z=res[0][2]
        res=p.getLinkState(self.bot_id,self.joints["uleg_to_knee_r"])
        rknee_z=res[0][2]

        if self.debug:
            print("lfoot_z=%s rfoot_z=%s lknee_z=%s rknee_z=%s"%(lfoot_z,rfoot_z,lknee_z,rknee_z))

        rews=[0]*8

        rews[0]=1

        pitch=obs[0]
        if self.debug:
            print("pitch=%s"%pitch)
        pitch_diff=abs(pitch)
        rews[1]=0.1*(math.exp(-3*pitch_diff)-1)

        force_foot_l=0
        force_foot_r=0
        force_other=0
        points=p.getContactPoints()
        for pt in points:
            #print("  %s"%(pt,))
            i=pt[4]
            pos=pt[6]
            norm=pt[7]
            force=pt[9]
            #print(" joint=%s force=%s pos=%s norm=%s"%(joint_name,force,pos,norm))
            if i==self.joints["lleg_to_foot_l"]:
                force_foot_l+=force
            elif i==self.joints["lleg_to_foot_r"]:
                force_foot_r+=force
            else:
                force_other+=force
        if self.debug:
            print("force_other=%s"%force_other)
            print("force_foot_l=%s"%force_foot_l)
            print("force_foot_r=%s"%force_foot_r)
        rews[2]=-0.1 if not force_foot_l else 0
        rews[3]=-0.1 if not force_foot_r else 0
        rews[4]=-0.1 if force_other else 0

        height_diff=abs(0.55-height)
        rews[5]=0.1*(math.exp(-height_diff*10.0)-1)
        if self.debug:
            print("height=%s"%height)

        speed_x=abs(obs[5])
        if self.debug:
            print("speed_x",speed_x)
        rews[6]=0.1*(math.exp(-speed_x*2.0)-1)

        prev_action=self.all_actions[-1] if self.all_actions else None
        if prev_action is not None:
            action_diff=np.linalg.norm(np.array(action)-np.array(prev_action))
            if self.debug:
                print("action_diff=%s prev_action=%s action=%s"%(action_diff,prev_action,action))
        else:
            action_diff=0
        rews[7]=0.1*(math.exp(-action_diff*5)-1)

        """
        speed_yaw=abs(obs[4])
        if self.debug:
            print("speed_yaw",speed_yaw)
        rews[7]=0.1*(math.exp(-speed_yaw*4)-1)
        """

        """
        power=sum([abs(t) for t in taus])
        if self.debug:
            print("taus",taus)
            print("power",power)
        rews[5]=0.2*(math.exp(-power*0.05)-1)

        prev_action=self.all_actions[-1] if self.all_actions else None
        if prev_action is not None:
            action_diff=np.linalg.norm(np.array(action)-np.array(prev_action))
            if self.debug:
                print("action_diff=%s prev_action=%s action=%s"%(action_diff,prev_action,action))
        else:
            action_diff=0
        rews[3]=0.2*(math.exp(-action_diff*5)-1)

        speed=obs[5:7]
        speed_diff=np.linalg.norm(speed)
        if self.debug:
            print("speed",speed,"speed_diff",speed_diff)
        rews[2]=0.1*(math.exp(-speed_diff*2.0)-1)

        yaw_speed=obs[4]
        yaw_speed_diff=abs(yaw_speed)
        if self.debug:
            print("yaw speed",yaw_speed,"yaw_speed_diff",yaw_speed_diff)
        rews[3]=0.15*(math.exp(-yaw_speed_diff*4)-1)

        yaw_diff=abs(yaw)
        if self.debug:
            print("yaw",yaw,"yaw_diff",yaw_diff)
        rews[4]=0.15*(math.exp(-yaw_diff*2)-1)

        roll_diff=abs(obs[1])
        rews[1]=math.exp(-3*roll_diff)

        pitchv_diff=abs(obs[2])
        rews[2]=math.exp(-0.1*pitchv_diff)

        rollv_diff=abs(obs[3])
        rews[3]=math.exp(-0.1*rollv_diff)

        yawv_diff=abs(obs[4])
        rews[4]=math.exp(-0.1*yawv_diff)

        torque=abs(obs[10])+abs(obs[13])+abs(obs[16])+abs(obs[19])
        rews[5]=math.exp(-0.1*torque)

        if len(self.all_actions)>=2:
            prev_action=self.all_actions[-2]
            action_diff=0
            for i in range(len(action)):
                action_diff+=abs(action[i]-prev_action[i])
        else:
            action_diff=0
        rews[6]=math.exp(-action_diff)
        """

        if self.debug:
            print("rews",rews)
        rew=sum(rews)
        self.all_rews.append(rews)

        done=False
        info={}

        self.step_counter += 1
        if self.step_counter>=self.max_episode_len:
            done=True
        if height<self.min_z or height>self.max_z:
            done=True
        #if self.step_counter-self.last_height_reached>80: # XXX
        #    done=True
        #if self.step_counter>80 and height<0.45: # XXX
        #if self.step_counter>40 and height<0.45: # XXX
        #    done=True
        #if abs(pos[0])>self.max_x or abs(pos[1])>self.max_y:
        ##    done=True
        #pitch=obs[0]
        #if abs(pitch)>self.max_pitch:
        #    done=True
        if self.step_counter>40 and force_other:
            done=True
        if done and not self.done:
            self.done=True
            if self.debug:
                fig,axs=plt.subplots(4,3)
                #fig.set_size_inches(20, 16)
                fig.set_size_inches(80, 30)

                pitch=[o[0] for o in self.all_obs]
                roll=[o[1] for o in self.all_obs]
                axs[0][0].set_title("Orientation")
                axs[0][0].plot(pitch,label="pitch")
                axs[0][0].plot(roll,label="roll")
                axs[0][0].legend()

                pitch=[o[2] for o in self.all_obs]
                roll=[o[3] for o in self.all_obs]
                yaw=[o[4] for o in self.all_obs]
                axs[0][1].set_title("Angular Velocity")
                axs[0][1].plot(pitch,label="pitch")
                axs[0][1].plot(roll,label="roll")
                axs[0][1].plot(yaw,label="yaw")
                axs[0][1].legend()

                pitch=[o[5] for o in self.all_obs]
                roll=[o[6] for o in self.all_obs]
                yaw=[o[7] for o in self.all_obs]
                axs[0][2].set_title("Linear Velocity")
                axs[0][2].plot(pitch,label="x")
                axs[0][2].plot(roll,label="y")
                axs[0][2].plot(yaw,label="z")
                axs[0][2].legend()

                umot_l=[o[8] for o in self.all_obs]
                umot_r=[o[10] for o in self.all_obs]
                lmot_l=[o[12] for o in self.all_obs]
                lmot_r=[o[14] for o in self.all_obs]
                axs[1][0].set_title("Motor Position")
                axs[1][0].plot(umot_l,label="umot_l")
                axs[1][0].plot(umot_r,label="umot_r")
                axs[1][0].plot(lmot_l,label="lmot_l")
                axs[1][0].plot(lmot_r,label="lmot_r")
                axs[1][0].legend()

                umot_l=[o[9] for o in self.all_obs]
                umot_r=[o[11] for o in self.all_obs]
                lmot_l=[o[13] for o in self.all_obs]
                lmot_r=[o[15] for o in self.all_obs]
                axs[1][1].set_title("Motor Speed")
                axs[1][1].plot(umot_l,label="umot_l")
                axs[1][1].plot(umot_r,label="umot_r")
                axs[1][1].plot(lmot_l,label="lmot_l")
                axs[1][1].plot(lmot_r,label="lmot_r")
                axs[1][1].legend()

                umot_l=[o[0] for o in self.all_torques]
                umot_r=[o[1] for o in self.all_torques]
                lmot_l=[o[2] for o in self.all_torques]
                lmot_r=[o[3] for o in self.all_torques]
                hmot_l=[o[4] for o in self.all_torques]
                hmot_r=[o[5] for o in self.all_torques]
                tau_max=[self.max_torque for o in self.all_torques]
                tau_min=[-self.max_torque for o in self.all_torques]
                axs[1][2].set_title("Motor Torque")
                axs[1][2].plot(umot_l,label="umot_l")
                axs[1][2].plot(umot_r,label="umot_r")
                axs[1][2].plot(lmot_l,label="lmot_l")
                axs[1][2].plot(lmot_r,label="lmot_r")
                axs[1][2].plot(lmot_l,label="hmot_l")
                axs[1][2].plot(lmot_r,label="hmot_r")
                axs[1][2].plot(tau_max,label="max")
                axs[1][2].plot(tau_min,label="min")
                axs[1][2].legend()

                umot_l=[a[0] for a in self.all_actions]
                umot_r=[a[1] for a in self.all_actions]
                lmot_l=[a[2] for a in self.all_actions]
                lmot_r=[a[3] for a in self.all_actions]
                hmot_l=[0 for a in self.all_actions]
                hmot_r=[0 for a in self.all_actions]
                axs[2][0].set_title("Action Pos")
                axs[2][0].plot(umot_l,label="umot_l")
                axs[2][0].plot(umot_r,label="umot_r")
                axs[2][0].plot(lmot_l,label="lmot_l")
                axs[2][0].plot(lmot_r,label="lmot_r")
                axs[2][0].plot(lmot_l,label="hmot_l")
                axs[2][0].plot(lmot_r,label="hmot_r")
                axs[2][0].legend()

                """
                umot_l=[a[1] for a in self.all_actions]
                umot_r=[a[4] for a in self.all_actions]
                lmot_l=[a[7] for a in self.all_actions]
                lmot_r=[a[10] for a in self.all_actions]
                hmot_l=[a[13] for a in self.all_actions]
                hmot_r=[a[16] for a in self.all_actions]
                axs[2][1].set_title("Action Kp")
                axs[2][1].plot(umot_l,label="umot_l")
                axs[2][1].plot(umot_r,label="umot_r")
                axs[2][1].plot(lmot_l,label="lmot_l")
                axs[2][1].plot(lmot_r,label="lmot_r")
                axs[2][1].plot(lmot_l,label="hmot_l")
                axs[2][1].plot(lmot_r,label="hmot_r")
                axs[2][1].legend()

                umot_l=[a[2] for a in self.all_actions]
                umot_r=[a[5] for a in self.all_actions]
                lmot_l=[a[8] for a in self.all_actions]
                lmot_r=[a[11] for a in self.all_actions]
                hmot_l=[a[14] for a in self.all_actions]
                hmot_r=[a[17] for a in self.all_actions]
                axs[2][2].set_title("Action Kd")
                axs[2][2].plot(umot_l,label="umot_l")
                axs[2][2].plot(umot_r,label="umot_r")
                axs[2][2].plot(lmot_l,label="lmot_l")
                axs[2][2].plot(lmot_r,label="lmot_r")
                axs[2][2].plot(lmot_l,label="hmot_l")
                axs[2][2].plot(lmot_r,label="hmot_r")
                axs[2][2].legend()
                """

                fixed=[r[0] for r in self.all_rews]
                pitch=[r[1] for r in self.all_rews]
                force_foot_l=[r[2] for r in self.all_rews]
                force_foot_r=[r[3] for r in self.all_rews]
                force_other=[r[4] for r in self.all_rews]
                height=[r[5] for r in self.all_rews]
                speed_x=[r[6] for r in self.all_rews]
                act_diff=[r[7] for r in self.all_rews]
                """
                power=[r[5] for r in self.all_rews]
                speed=[r[3] for r in self.all_rews]
                yaw=[r[4] for r in self.all_rews]
                """
                total=[sum(r) for r in self.all_rews]
                axs[3][0].set_title("Rewards")
                axs[3][0].plot(fixed,label="fixed")
                axs[3][0].plot(pitch,label="pitch")
                axs[3][0].plot(force_foot_l,label="force_foot_l")
                axs[3][0].plot(force_foot_r,label="force_foot_r")
                axs[3][0].plot(force_other,label="force_other")
                axs[3][0].plot(height,label="height")
                axs[3][0].plot(speed_x,label="speed_x")
                axs[3][0].plot(act_diff,label="act_diff")
                """
                axs[3][0].plot(speed_yaw,label="speed_yaw")
                axs[3][0].plot(power,label="power")
                axs[3][0].plot(yaw_speed,label="yaw_speed")
                axs[3][0].plot(yaw,label="yaw")
                axs[3][0].plot(yaw_speed,label="yaw_speed")
                axs[3][0].plot(act_diff,label="act_diff")
                axs[3][0].plot(speed,label="speed")
                """
                axs[3][0].plot(total,label="total")
                axs[3][0].legend()

                """
                pitch=[r[0] for r in self.all_rews]
                roll=[r[1] for r in self.all_rews]
                axs[3][1].set_title("Orientation Rewards")
                axs[3][1].plot(pitch,label="pitch")
                axs[3][1].plot(roll,label="roll")
                axs[3][1].legend()

                pitch_v=[r[2] for r in self.all_rews]
                roll_v=[r[3] for r in self.all_rews]
                yaw_v=[r[4] for r in self.all_rews]
                torque=[r[5] for r in self.all_rews]
                action_d=[r[6] for r in self.all_rews]
                axs[3][2].set_title("Other Rewards")
                axs[3][2].plot(pitch_v,label="pitch_v")
                axs[3][2].plot(roll_v,label="roll_v")
                axs[3][2].plot(yaw_v,label="yaw_v")
                axs[3][2].plot(torque,label="torque")
                axs[3][2].plot(action_d,label="action_d")
                axs[3][2].legend()
                """

            #plt.show()
            plt.savefig("z1bot_hist.png")

        self.all_actions.append(action)
        return np.array(self.observation).astype(np.float32), rew, done, info

    def render(self):
        pass

    def _get_state(self):
        return self.observation

    def close(self):
        p.disconnect()
