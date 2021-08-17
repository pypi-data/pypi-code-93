# -*- coding: utf-8 -*-

from mod.common.component.baseComponent import BaseComponent

class ParticleControlComp(BaseComponent):
    def Play(self):
        # type: () -> bool
        """
        播放粒子特效
        """
        pass

    def Stop(self):
        # type: () -> bool
        """
        停止粒子播放
        """
        pass

    def SetRelative(self, relative):
        # type: (bool) -> bool
        """
        当粒子绑定了entity或骨骼模型时，发射出的粒子使用entity坐标系还是世界坐标系。与mcstudio特效编辑器中粒子的“相对挂点运动”选项功能相同。
        """
        pass

    def SetLayer(self, layer):
        # type: (int) -> bool
        """
        粒子默认层级为1，当层级不为1时表示该特效开启特效分层渲染功能。特效（粒子和帧动画）分层渲染时，层级越高渲染越靠后，层级大的会遮挡层级低的，且同一层级的特效会根据特效的相对位置产生正确的相互遮挡关系。
        """
        pass

    def SetFadeDistance(self, fadeDistance):
        # type: (float) -> bool
        """
        设置粒子开始自动调整透明度的距离。粒子与摄像机之间的距离小于该值时会自动调整粒子的透明度，距离摄像机越近，粒子越透明
        """
        pass

    def SetUsePointFiltering(self, enable):
        # type: (bool) -> bool
        """
        设置粒子材质的纹理滤波是否使用点滤波方法。默认为使用双线性滤波
        """
        pass

