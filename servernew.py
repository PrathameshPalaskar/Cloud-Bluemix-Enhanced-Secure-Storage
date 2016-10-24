import MySQLdb,os
from flask import Flask,render_template,request
global u_id

app=Flask(__name__)
#app.config['UPLOAD_FOLDER']= 'UPLOADER_FOLDER/'
port = int(os.getenv('VCAP_APP_PORT', 5000))

db=MySQLdb.connect(host="us-cdbr-iron-east-04.cleardb.net",user="*************",passwd="*******",port=3306,db="****")
cur=db.cursor()



@app.route('/',methods=['GET'])
def run():
	return render_template("index.html")

#Validation of user id and password
@app.route('/index',methods=['POST'])	
def index():
	l=request.form['login']
	p=request.form['passwd']
	sql=("Select User_ID from user_details where User_name=%s and User_password=%s")
	query_parameters=(l,p)
	cur.execute(sql,query_parameters)
	result=cur.fetchall()
	global u_id
	for row in result:
		u_id=row[0]		
	print "%s" %u_id
	return render_template("upload.html")

#Upload the file with file size and versioning with description
@app.route('/upload',methods=['POST'])
def upload():
	file_list=[]
	file1=request.files['file']
	list_size=[]
	global u_id
	f_s=os.stat(file1.filename).st_size

	sql="select File_name from file_details where u_id=%s"
	cur.execute(sql,str(u_id))
	res=cur.fetchall()
	for i in res:
		file_list.append(i[0])
	for i in file_list:
		if(file1.filename==i):
			sql4="select version from file_details where File_name=%s and u_id=%s order by version desc"
			arg=(file1.filename,str(u_id))			
			cur.execute(sql4,arg)
			ver=cur.fetchone()
			v1=ver[0]
			print type(v1)
			v=v1+1
	size=1048576
	t_size=0
	sql5="insert into user_quota (u_id,quota) values (%s,%s)"
	rg=(str(u_id),str(size))
	cur.execute(sql5,rg)
	db.commit()
	sql6="select file_size from file_details where u_id=%s"
	cur.execute(sql6,str(u_id))
	si=cur.fetchall()
	for j in si:
		list_size.append(j[0])
	print list_size
	for k in list_size:
		t_size=t_size+int(k)
	if(t_size<size):
		sql7="update user_quota set quota=%s where u_id=%s"
		p=(str(t_size),str(u_id))		
		cur.execute(sql7,p)
		des=request.form['desc']
		thedata = open(file1.filename, 'rb').read()
		sql1= "INSERT INTO file_details (u_id,file_name,file_content,file_desc,file_size,version) values (%s,%s,%s,%s,%s,%s)"
		args=(str(u_id),file1.filename,thedata,des,str(f_s),str(v))
		cur.execute(sql1,args)
		db.commit()
	else:
		print "quota full"
	sql2="Select file_content from file_details where file_name=%s"
	a=str(file1.filename)
	cur.execute(sql2,a)
	result=cur.fetchall()	
	for row in result:
		filew=row[0]
	with open(a,'w') as f:
		f.write(filew)
	db.close()
	return render_template("d.html")

if __name__=="__main__":
	app.run(host='127.0.0.1', port=port,debug=True)
