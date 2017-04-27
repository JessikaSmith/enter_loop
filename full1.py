MAIN_IMAGE_PATH = 'images\\logo.gif'
END_IMAGE_PATH = 'images\\end.gif'
REG_FAILED_IMAGE_PATH = 'images\\registration_failed.gif'
ID_FAILED_IMAGE_PATH = 'images\\id_failed.gif'

FIRST_ALERT_TIME = 10
SECOND_ALERT_TIME = 5
ID = 1


# post запрос
from grab import Grab
import sys
from config import *
import time 
# import socket
from tkinter import *
import dropbox
# id оборудования
equip_id = ID

def mainApp():
	root = Tk()
	w, h = root.winfo_screenwidth(), root.winfo_screenheight() # возвращает высоту и ширину экрана в px
	root.overrideredirect(1)
	root.geometry("%dx%d+0+0" % (w, h))
	root.configure(background='white')
	root.wm_attributes("-topmost", 1)
	photo = PhotoImage(file=MAIN_IMAGE_PATH)
	label = Label(root,image=photo)
	label.image=photo
	label.pack(fill='both',expand = "yes")
	
	login = Entry(label,width=50,bd=5)
	login.place(relx=0.5, rely=0.45, anchor=CENTER)
	login.insert(0, "Введите логин")
	login.focus_set()
	
	password = Entry(label,width=50,bd=5, show='*')
	password.place(relx=0.5, rely=0.5, anchor=CENTER)
	password.insert(0, "default")
	password.focus_set()
		
	def check():
		g = Grab()
		resp = g.go('http://fablab.ifmo.ru/wp-login.php?redirect_to=index.php')
		global user_login 
		user_login = login.get()
		g.doc.set_input('log', user_login)
		g.doc.set_input('pwd', password.get())
		g.doc.submit()
		print(g.response.url)
		print(type(g.response.unicode_body()))
		if g.response.url == 'http://fablab.ifmo.ru/wp-login.php':   # условие(?)
			password.delete(0,'end')
		else:
			root.destroy()
			
	b = Button(label, text="Войти", width=10, command=check, relief=RIDGE)
	b.place(relx=0.5, rely=0.55, anchor=CENTER)
	root.lift()
	root.mainloop()
 
def popup(min):
	toplevel = Tk()
	toplevel.wm_attributes("-topmost", 1)
	toplevel.focus() 
	label1 = Label(toplevel, text='Осталось '+str(min)+' минут', height=0, width=50)
	label1.pack()	
	
	def close_after_s():
		toplevel.destroy()
		
	toplevel.after(3000, close_after_s)	
	toplevel.mainloop()

def end(id):
	image_dict = {1: END_IMAGE_PATH, 2: REG_FAILED_IMAGE_PATH, 3: ID_FAILED_IMAGE_PATH}
	IMAGE_PATH = image_dict[id]
	toplevel = Tk()
	w, h = toplevel.winfo_screenwidth(), toplevel.winfo_screenheight() 
	toplevel.overrideredirect(1)
	toplevel.geometry("%dx%d+0+0" % (w, h))
	toplevel.wm_attributes("-topmost", 1)
	toplevel.focus() 
	photo = PhotoImage(file=IMAGE_PATH)
	label = Label(toplevel,image=photo)
	label.image=photo
	label.pack(fill='both',expand = "yes")
	
	def close_after_s():
		toplevel.destroy()
		
	toplevel.after(5000, close_after_s)	
	toplevel.mainloop()
	
def get_end_time():
	global user_login
	g = Grab()
	print(user_login)
	resp = g.go('http://fablab.ifmo.ru/out.php?login='+user_login)
	resp_text = resp.unicode_body()
	global equip_id
	print(resp_text)
	if resp_text == 'Fail':   #i*hh:mm/
		return 2
	else:
		text = resp_text.split('/')
		text = [m for m in text if not m == '']
		for dt in text:
			nt = dt.split('*')
			if int(nt[0]) == equip_id:
				end_time = nt[1].split(':')
				# разница в секундах между текущим и конечным временем
				e_t = int(end_time[0])*60*60 + int(end_time[1])*60 - ((time.localtime().tm_hour)*60*60 + time.localtime().tm_min*60)
				return e_t
		return 3


# Добавить access_token		
def leave_comment():
	access_token = '' 
	client = dropbox.client.DropboxClient(access_token)
	toplevel = Tk()
	toplevel.wm_attributes("-topmost", 1)
	toplevel.focus() 
	comment = Entry(toplevel,width=50,bd=5)
	comment.place(relx=0.5, rely=0.45, anchor=CENTER)
	comment.insert(0, "Введите логин")
	comment.focus_set()
	tx = Text(font=('times',12),width=50,height=15,wrap=WORD)
	tx.insert(1.0,'Оставьте свой комментарий') 
	tx.pack(expand=YES,fill=BOTH) 
	
	def ex():
		toplevel.destroy()
	
	def send():
		global user_login
		text = tx.get("1.0",END)
		response = client.put_file(str(user_login)+' '+ str(round(time.time()))+'.txt', text.encode('utf-8'))
		toplevel.destroy()
	
	m = Button(toplevel, text="Отмена", width=10, command=ex)
	m.pack(side=RIGHT)
	b = Button(toplevel, text="Отправить", width=10, command=send)
	b.pack(side=RIGHT)
	
	toplevel.mainloop()	
	
while(True):  
	user_login = 'r'
	mainApp()
	END_TIME = get_end_time()
	if END_TIME in [2,3]:
		end(END_TIME)
		continue
	END_TIME = END_TIME + time.time()
	time.sleep(END_TIME - time.time() - 60*FIRST_ALERT_TIME) # за 10 мин.
	popup(FIRST_ALERT_TIME)
	time.sleep(END_TIME - time.time() - 60*SECOND_ALERT_TIME) # за 5 мин.
	popup(SECOND_ALERT_TIME)
	end(1)
	leave_comment()
	break
