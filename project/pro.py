from flask import Flask,render_template,request,redirect,url_for
app = Flask(__name__)
import numpy 
import re
import pygal
def matchQuery(q):
 r = re.match(r"(\d+)-(\d+)", q)
 if r:
    return 1
 else:
    return 0
def sjf(num, mat) :
 end, val=0,0
 mat[0][3] = mat[0][1] + mat[0][2]
 mat[0][5] = mat[0][3] - mat[0][1] 
 mat[0][4] = mat[0][5] - mat[0][2] 
 for i in range (1,num):
    end = mat[i-1][3]
    low = mat[i][2]
    for j in range(i,num) :  
        if end >= mat[j][1] and low >= mat[j][2]:
            low = mat[j][2]
            val = j
    mat[val][3] = end + mat[val][2]
    mat[val][5] = mat[val][3] - mat[val][1]
    mat[val][4] = mat[val][5] - mat[val][2]
    for  k in range (6) :
       end = mat[val][k]
       mat[val][k] = mat[i][k] 
       mat[i][k]=end
 return mat
def RR(num,mat,time_quantum):
    time_quantum=int(time_quantum)
    aa=[0]*num
    rt=[0]*num
    time=0
    for i in range(num):
        rt[i]=mat[i][2]
        aa[i]=mat[i][1]
    i=0
    remain=num
    while remain!=0:
        for j in range(0,num):
            if aa[i]>aa[j]and rt[j]!=0:
                 i=j
        if rt[i]<=time_quantum and  rt[i]>0:
            time += rt[i]
            rt[i]=0
            remain=remain-1
            mat[i][5]=time-mat[i][1]
            mat[i][4]=mat[i][5]-mat[i][2]
        elif rt[i]>0 :
            rt[i] -= time_quantum
            time += time_quantum
            aa[i]=time
        if(i == num-1):
            i=0
        else:
            i=i+1
    return mat
    
def srtf(num,mat):
    rt= [0] * num
    for i in range (num):
      rt[i]=mat[i][2]
    remain = 0
    t = 0
    minm = 10000
    short = 0
    while (remain != num): 
        for j in range(num): 
            if ((mat[j][1] <= t) and (rt[j] < minm) and rt[j] > 0): 
                minm = rt[j] 
                short = j 
        rt[short] -= 1
        minm = rt[short] 
        if (minm == 0): 
            minm = 10000
        if (rt[short] == 0): 
            remain += 1
            end = t + 1
            mat[short][4] = (end - mat[short][1] -mat[short][2]) 
            mat[short][5]=mat[short][4]+mat[short][2]
        t += 1
    return mat
   
def fcfs(num,mat):
    start=[]
    start.append(mat[0][1])
    y=0
    for i in range(num):
        y=mat[i][2]+y
        start.append(y)
    for i in range (num):
        y=start[i]-mat[i][1]
        mat[i][4]=y
    for i in range (num):
        y=(start[i+1]-start[i])+mat[i][4]
        mat[i][5]=y
    return mat

@app.route('/', methods=['GET','POST'])
def form():
 if request.method == 'POST':
    arrival =request.form['arrival'].replace('-',' ').split(' ')
    brust =request.form['brust'].replace('-',' ').split(' ')
    idp =request.form['idp'].replace('-',' ').split(' ')
    num=int(request.form['num'])
    if num==len(brust) and num==len(arrival) and num==len(idp):
     if matchQuery(request.form['brust']) and matchQuery(request.form['arrival']) and matchQuery(request.form['idp']):
      w, h = 6, num
      mat = [[0 for x in range(w)] for y in range(h)]
      for  i in range (num) :
        mat[i][0]=int(idp[i])
        mat[i][1]=int(arrival[i])
        mat[i][2]=int(brust[i])
      a = numpy.array(mat)
      m= a[a[:,1].argsort()]
    
      if request.form['btn'] == 'FCFS':
        mat = fcfs(num,m)
        l= numpy.sum(m,axis=0)
        avgWaiting=round(l[4]/num,3)
        avgTurnaround=round(l[5]/num,3)
        return render_template('form.html',q=range(num),mat=mat,w=avgWaiting,t=avgTurnaround,q1=num-1)
    
      if request.form['btn'] == 'SJF':
        mat= sjf(num,m)
        l= numpy.sum(m,axis=0)
        avgWaiting=round(l[4]/num,3)
        avgTurnaround=round(l[5]/num,3)
        return render_template('form.html',q=range(num),mat=mat,w=avgWaiting,t=avgTurnaround,q1=num-1)
      
      if request.form['btn'] == 'RR':
        quantum=int(request.form['quantum'])
        mat= RR(num,m,quantum)
        l= numpy.sum(m,axis=0)
        avgWaiting=round(l[4]/num,3)
        avgTurnaround=round(l[5]/num,3)
        return render_template('form.html',q=range(num),mat=mat,w=avgWaiting,t=avgTurnaround,q1=num-1)
      
      if request.form['btn'] == 'SRTF':
        mat= srtf(num,m)
        l= numpy.sum(m,axis=0)
        avgWaiting=round(l[4]/num,3)
        avgTurnaround=round(l[5]/num,3)
        return render_template('form.html',q=range(num),mat=mat,w=avgWaiting,t=avgTurnaround,q1=num-1)
      if request.form['btn'] == 'ALL':
            quantum=int(request.form['quantum'])
            mat2= numpy.array(sjf(num,m))
            mat1 = numpy.array(fcfs(num,m))
            mat4= numpy.array(RR(num,m,quantum))
            mat3=numpy.array(srtf(num,m))
            line_chart1 = pygal.Bar()
            line_chart2= pygal.Bar()
            line_chart1.x_labels=map(str,range(1,num+1))
            line_chart1.add('FCFS',mat1[:,5].astype(float))
            line_chart1.add('SJF',mat2[:,5].astype(float))
            line_chart1.add('SRTF',mat3[:,5].astype(float))
            line_chart1.add('RR',mat4[:,5].astype(float))
            line_chart1.title = 'Turnaround time for four algorithms'
            line_chart2.x_labels=map(str,range(1,num+1))
            line_chart2.add('FCFS',mat1[:,4].astype(float))
            line_chart2.add('SJF',mat2[:,4].astype(float))
            line_chart2.add('SRTF',mat3[:,4].astype(float))
            line_chart2.add('RR',mat4[:,4].astype(float))
            line_chart2.title = 'Waiting time for four algorithms'
            graph_data1 = line_chart1.render_data_uri()
            graph_data2 = line_chart2.render_data_uri()
            return render_template('form.html',graph_data1 = graph_data1,graph_data2=graph_data2,f=1)
    else:
        p='error : please enter in form '
        return render_template('form.html',p=p)
 return render_template('form.html')

if __name__ == '__main__':
 app.run(debug = True)