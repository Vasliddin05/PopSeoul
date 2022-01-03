# -*- coding: utf-8 -*-
"""
Created on Sat Jan  1 21:47:20 2022

@author: joebr
"""

introduction=\
"\n<소개>\n서울 생활인구란 서울시와 KT가 공공빅데이터와 통신데이터를 이용하여 \
추계한 서울의 특정지역, 특정시점에 존재하는 모든 인구입니다. \
pop생활인구는 서울시에서 제공하는 Open API를 통해 내려받은 \
행정동별 생활인구 데이터를 보다 가볍고 보기쉽게 가공하는 응용 프로그램입니다. \
날짜 범위와 행자부행정동 코드를 입력하면 원하는 범위의 일주일간/시간별 \
(성별, 인구 통합)생활인구를 csv파일과 그래프로 정리해 제공합니다.\n"

import pandas as pd
import matplotlib.pyplot as plt
import pickle
import urllib.request 
import json 
from datetime import date


#fixed variable

st0="http://openapi.seoul.go.kr:8088//json/SPOP_LOCAL_RESD_DONG/1/30/"

#basic functions

def arr(a,b,c,d):
    d.append(a)
    o= a+c
    if o > b:
        return d
    else:
        return arr(o, b, c, d)

def shat(ro):
    st= str(ro)
    yy= int(st[0:4])
    mm= int(st[4:6])
    dd= int(st[6:8])
    return date(yy, mm, dd).weekday()

def shat2(ro):
    st= str(ro)
    yy= st[0:4]
    mm= st[4:6]
    dd= st[6:8]
    return yy+'.'+mm+'.'+dd+'.'

def mx(ls):
    mx0=max(ls)
    mx1=round(mx0 * 0.7)
    mxc=len(str(mx1))
    mxcn=-mxc+1
    mx2=round(mx0 * 1.2, mxcn)
    return mx2

def ti(df):
    daterange=list(df)
    st=min(daterange)
    ed=max(daterange)
    pe=shat2(st)+' ~ '+shat2(ed)
    return pe

def two_dig(n):
    m=str(n)
    if len(m) == 1:
        t= '0' + m 
        return t
    else:
        return m

def call(st,qu):
    response = urllib.request.urlopen(st)
    json_str = response.read().decode("utf-8")
    json_object = json.loads(json_str)
    j = pd.io.json.json_normalize(json_object['SPOP_LOCAL_RESD_DONG']['row'])
    j1 = j[qu]
    return j1

def testcall(dali,qu,s):
    foo=[]
    for i in dali:
        r=s + i + '/01/' + '11170530'
        try:
            bar=call(r,qu)
            foo.append(i[4:6])
        except:
            continue
    return foo

    
#core functions

def check_date(qu,s,n):
    t=date.today()
    ty=t.year
    yli=[]
    yx=[]
    zx=[]
    for i in range(n):
        yli.append(str(ty-i))
        yx.append([])
        
    for i in range(n):
        for k in range(1,13):
            yx[i].append(yli[i]+two_dig(k)+'01')
        zx.append(testcall(yx[i],qu,s))
    
    for i in range(n):
        print(yli[i] + '년 조회 가능 달:')
        print(zx[i])
    print('')

def load(ds,de,lo,qu,st2):
    dp=pd.date_range(str(ds),str(de))
    days=dp.strftime("%Y%m%d").tolist()
    dset=[]
    for i in days:
        req=st2 + str(i) + '/%20/' + str(lo)
        req_s=st0 + str(i) + '/%20/' + str(lo) #키를 숨긴 프린트용
        print(req_s)
        j3=call(req,qu)
        dset.append(j3)
    popa=pd.concat(dset, ignore_index=True)
    poplocx=popa.rename(columns = {"STDR_DE_ID":"date", "TMZON_PD_SE":"time", "ADSTRD_CODE_SE":"loc", "TOT_LVPOP_CO":"population"})
    poplocx['wd']=0
    poplocx.wd= poplocx.date.apply(shat)*100 + 100 + poplocx.time.apply(int)
    print(poplocx.head())
    return poplocx

def weekday_average(a):
    wt=[]
    avr=[]
    for i in range(7):
        for j in range (24):
            wt.append(100*i + j + 100 )
    for i in wt:
        m= a.population[a.wd == i].values
        n= 0
        for j in m:
            n = n + float(j)
        n = n/len(m)
        avr.append(n)
    avr=avr+avr[0:1]
    return avr

def make_graph(df):
    
    #기본틀
    peri=ti(df.date)
    print("요일별/시간별 인구수 평균을 구하는 중...")
    li=weekday_average(df)
    gtop=mx(li)
    fig, ax = plt.subplots(figsize=(21,7))
    ax.plot(li, '-', color='navy')
    plt.axis([0,167,0,gtop])
    plt.title('Date: '+peri, loc='right', size=8)
    
    print("그래프를 그리는 중...")
    #배경색
    for i in arr(-6, 168, 24, []):
        j = i + 12
        plt.fill([i,i,j,j],[0,gtop,gtop,0],color='lightgrey', alpha=0.5)
    
    #눈금
    xl=['00','06','12','18']*7+['00']
    xsubl=['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
    for i, s in enumerate(xl):
        if s =='12':
            xl[i]=s+'\n\n'+xsubl[0]
            xsubl=xsubl[1:]
    
    ax.set_xticks(arr(0,168,6,[]),minor=True)
    ax.set_xticklabels(xl, minor=True)
    ax.tick_params(axis='x', which='minor', labelsize=10, pad=4, length=4)
    plt.grid(True, axis='x', color='silver', which='minor')

    ax.set_xticks(arr(0.1,169,24,[]), minor=False)
    ax.tick_params(axis='x', which='major', labelbottom=False, length=8, width=2)
    plt.grid(True, axis='x', color='dimgrey', which='major')

    plt.grid(True, axis='y')
    plt.show()
    
    lid=pd.DataFrame(data=li, index=(range(len(li))), columns=(['poplulation_average']))
    return lid

#menu

def print_menu():
    print('<메뉴>')
    print("1. 생활인구 데이터 출력")
    print("2. 재출력")
    print("3. 설정")
    print("4. 종료")
    m = input("입력: ")
    return int(m)
    
def print_setting1():
    global setting
    print('두가지 변수를 조정할 수 있습니다')
    print('1. API key')
    print('2. 인구분류코드')
    ch=int(input('입력: '))
    
    if ch == 1:
        newp = input('새로운 키를 입력하십시오: ')
        setting['key']=newp
    elif ch == 2:
        newp = input('새로운 인구분류코드를 입력하십시오(default:TOT_LVPOP_CO): ')
        setting['qu0'][3]=newp
    
    with open('pop_setting.txt', 'wb') as f:
        pickle.dump(setting, f)
        print('저장됨')

def run():
    global setting
    with open('pop_setting.txt', 'rb') as f:
        setting=pickle.load(f)
    key=setting['key']
    qu0=setting['qu0']
    while 1:
        menu = print_menu()
        if menu == 1:
            st1=st0[0:32]+key+st0[32:]
            print('지난 3년간 데이터 조회 가능한 일자 조사 중...\n')
            print('2022년 현재 조회 불가능한 날짜가 있습니다. 다음에 표시되는 달 안에서 조사를 수행하시길 추천드립니다.\n')
            check_date(qu0, st1, 3)
            da1=input("시작일(ex. 20210101): ")
            da2=input("종료일(ex.20210131): ")
            lo1=input("행정동코드(ex. 11410585): ")
            
            print("생활인구 데이터 다운로드 중...")
            try:
                poploc=load(da1, da2, lo1, qu0, st1)
            except:
                print('다운로드 중 오류가 발생했습니다.')
                return run() 
            print("백업 중...")
            with open ('saveddf default.txt', 'wb') as f:
                pickle.dump(poploc, f)
            poploc.to_csv('savedtable default.csv',sep=',')
            av_table=make_graph(poploc)
            av_table.to_csv('savedavr default.csv',sep=',' )
            
        elif menu == 2:
            with open ('saveddf default.txt', 'rb') as f:
                poploc = pickle.load(f)
            make_graph(poploc)
        
        elif menu == 3:
            print_setting1()
            
        elif menu == 4:
            break
        
if __name__ == "__main__":
    print(introduction)
    run()