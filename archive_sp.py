import json, os, subprocess
from urllib import request, parse
import shutil,requests
import datetime
from concurrent.futures import ThreadPoolExecutor

b = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
array = ['','==','=']

root_dir = "sp_archive"
user_dir = ""

def encodeSeed(data):
    d = ''
    encoded = ''
    for p in range(0,len(data)):
        d = d + "{0:08b}".format(ord(data[p]))
    d=d+'0000'
    
    for k in range(len(d)//6):
        ha = int(d[k*6:k*6+6],2)
        encoded = encoded + b[ha]
    encoded = array[len(encoded)%3-1]+encoded
    encoded = encoded[::-1]
    return encoded

def get_comments(args):
    r = requests.post("https://mcseeds.mobi/seedscript_802.php", data=args[0], headers={"user-agent":"Minecraft%20Seeds%20Pro/2018.06.191148 CFNetwork/711.4.6 Darwin/14.0.0"})
    with open("./"+args[2]+"/"+args[1]+"/"+"comments.json",'w+') as f:
        f.write(r.text)

def get_url(args):
    for i in range(1,int(args[1])+1):
        url = args[0] + str(i) + ".jpg"
        r = requests.get(url, stream = True)
        r.raw.decode_content = True
        with open("./"+args[3]+"/"+args[2]+"_"+str(i)+".jpg",'wb') as f:
                    shutil.copyfileobj(r.raw, f)
    return 1

def getComments(user_dir):
    with open("./"+user_dir+"/userseeds.json") as data_file:    
        data = json.load(data_file)
    
    commenturls = []
    for x in range(0,len(data["seeds"])):
        seedid = data["seeds"][x]["id"]
        category = data["seeds"][x]["category"]
        ftchCom1 = '{"identifier":"0000000000000000000000000000000000000000"'
    
        full = ftchCom1 + ',' + '"seedid"' + ':' + '"' + seedid + '"' + ',"latestCmntID":0,"pop":500,"udid_new":"G:1647168470","commentsSort":"Newest","category":' + '"' + category + '"' + ',"start":0,"ageOfComments":"older"}'
        headers = {
    'User-Agent': 'Minecraft%20Seeds%20Pro/2018.06.191148 CFNetwork/711.4.6 Darwin/14.0.0',
    
    }
        form_data = {
        "fetchComments":encodeSeed(full)
    }
        commenturls.append((form_data,seedid,user_dir))
    print("DOWNLOADING COMMENTS")
    print("STARTING AT "+str(datetime.datetime.now()))
    with ThreadPoolExecutor(max_workers=20) as pool:
        response_list = list(pool.map(get_comments,commenturls))
        

def downloadImages(user_dir):
    with open("./"+user_dir+"/userseeds.json") as data_file:    
        data = json.load(data_file)
        
    imageurls = []
    for x in range(0,len(data["seeds"])):
        imageurl = ''
        a = 'https://mcseeds.mobi/seeds/imgrdrct.php?p=mcsp17&url=seeds/user_uploads/'
        b = data["seeds"][x]["platform"]
        bx = data["seeds"][x]["version"]
        c = data["seeds"][x]["date"]
        d = data["seeds"][x]["filename"]
        e = data["seeds"][x]["pictures"]
        id = data["seeds"][x]["id"]
        pics = "./"+user_dir+"/"+id
        for i in range(1,int(e)+1):
            if not os.path.exists(pics):
                os.makedirs(pics)
            if bx:
            
                imageurl = a + b + "/" + bx + "/" + c[0:4] + "/" + c[-5:] + "/" + d
            else:
                imageurl = a + b + "/" + c[0:4] + "/" + c[-5:] + "/" + d
            imageurls.append((imageurl,e,d,pics))
    print("DOWNLOADING IMAGES")
    print("STARTING AT "+str(datetime.datetime.now()))
    with ThreadPoolExecutor(max_workers=20) as pool:
        response_list = list(pool.map(get_url,imageurls))

def downloadUserSeeds(id,nick):
    
    udid = id
    user_dir = root_dir+"/"+nick
    getSeeds = '{"identifier":"ba3862215b3bdd84f9d366166e521a0a18d0fbdf","pop":5000,"fetchUdid":"'+udid+'","category":"Uploads","section":"myseeds","searchString":"","udid_new":"'+udid+'","version":"All","extraSortOptions":"anytime","start":0,"worldType":"","platform":"My seeds","sort":"new"}'
    print("DOWNLOADING USER SEEDS (POSTS/UPLOADS)")
    headers = {
    'User-Agent': 'Minecraft%20Seeds%20Pro/2018.06.191148 CFNetwork/711.4.6 Darwin/14.0.0',
    
}
    dataa = parse.urlencode({'getSeeds':encodeSeed(getSeeds)}).encode()
    print(encodeSeed(getSeeds))
    req =  request.Request('https://mcseeds.mobi/seedscript_805.php', data=dataa, headers=headers)
    resp = request.urlopen(req).read()

    file = open("./"+user_dir+"/userseeds.json", 'wb')
    file.write(resp)
    file.close()


def searchUser(user):
    usrSearch = user
    consData1 = '{"searchString":"' + usrSearch + '","identifier":"ba3862215b3bdd84f9d366166e521a0a18d0fbdf","start":0,"fetchUdid":"","pop":20,"udid_new":"G:1281940767"}'
    headers = {
    'User-Agent': 'Minecraft%20Seeds%20Pro/2018.06.191148 CFNetwork/711.4.6 Darwin/14.0.0',
    
}
    dataa = parse.urlencode({'get_users':encodeSeed(consData1)}).encode()
    req =  request.Request('https://mcseeds.mobi/seedscript_805.php', data=dataa, headers = headers)
    resp = request.urlopen(req)

    comJson = json.load(resp)
    direc = {}
    for x in range(0,len(comJson["users"])):
        direc[x] = comJson["users"][x]["udid"]
        
        print(str(x)+" "+comJson["users"][x]["udid"]+" "+comJson["users"][x]["nickname"]+" "+comJson["users"][x]["bios"])
    choice = input("Choose number from list->")
    nick = comJson["users"][int(choice)]["nickname"]
    user_dir = root_dir+"/"+nick
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
    else:
        print("ARCHIVE FOR THIS USER (SEEMS TO) ALREADY EXIST")
        exit()
    downloadUserSeeds(direc[int(choice)],nick)
    downloadImages(user_dir)
    getComments(user_dir)


if not os.path.exists(root_dir):
    os.makedirs(root_dir)
user = input("Input the username->")
searchUser(user)
#downloadImages(root_dir+"/"+"Frios10")
#getComments(root_dir+"/"+"Frios10")
