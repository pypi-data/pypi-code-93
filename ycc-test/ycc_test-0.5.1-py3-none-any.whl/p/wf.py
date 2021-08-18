import sys as s, time as t
def wf():
    print("正在关闭......\n5s后完毕")
    for i in range(1,6):    
        s.stdout.write("█")
        if i == 5:
            s.stdout.write("█" +str(i)+"s100%")
        s.stdout.flush()
        t.sleep(1)
    print("\n" + "已关闭")
    s.exit()
#wf()