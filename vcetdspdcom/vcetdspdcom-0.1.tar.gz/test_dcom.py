import matplotlib.pyplot as plt
from vcet-dsp-dcom import ask_modulation
##ASK Modulation
fs=1000
fc1=10
fc2=15
tb=0.1
sim_t=1
[y_output,m_message,c_carrier,t_time]=ask_modulation(fs,fc1,tb,sim_t)
plt.subplot(3,1,1)
plt.plot(t_time,m_message)
plt.subplot(3,1,2)
plt.plot(t_time,c_carrier)
plt.subplot(3,1,3)
plt.plot(t_time,y_output)
plt.show()
