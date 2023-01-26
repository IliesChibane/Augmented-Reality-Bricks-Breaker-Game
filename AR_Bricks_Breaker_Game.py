import cv2
import numpy as np
from random import randint   


global no_stop 
no_stop = True

def detect_inrange(image,surfacemin,surfacemax, lo, hi): #fonction faite en tp
    points=[]
    image=cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
    mask=cv2.inRange(image,lo,hi)
    mask=cv2.erode(mask,None,iterations=2)
    mask=cv2.dilate(mask,None,iterations=2)
    elements = cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[-2]
    elements = sorted(elements,key = lambda x:cv2.contourArea(x), reverse=True)
    for element in elements:
        if cv2.contourArea(element) > surfacemin and cv2.contourArea(element) < surfacemax:
            ((x,y),rayon)=cv2.minEnclosingCircle(element)
            points.append(np.array([int(x),int(y),int(rayon)]))
        else:
            break
    return image,mask,points

def game():
    #defining the ball & its steps
    dx, dy = 4,4 #vitesse du ballon
    x1,y1 = 90,150 #init top left
    x2,y2 = 100,160 #init bottom right
    bar_start = 50 #degré de décalage du paddle
    bar_lvl = 410 #niveau de hauteur du paddle
    bricks_start_x = 10 #début des bricks x
    bricks_start_y = 50 #début des bricks x
    #taille de la brick
    largeur_brick = 60 
    hauteur_brick =20
    largeur_paddle = 30
    hauteur_paddle=20
    #score du joueur
    pts=0
    #array containing brick coordinates
    bricks = []
    
    surfacemin, surfacemax = 5000,500000

    #définir nos bricks
    for i in range(4):
        bricks.append([])
        for j in range(18):
            bricks[i].append([]) 
        for j in range(18):
            new_brick_x = bricks_start_x + largeur_brick*j
            new_brick_y = bricks_start_y + hauteur_brick*i
            bricks[i][j] = str(new_brick_x)+"_"+str(new_brick_y)

    cap = cv2.VideoCapture(0)
    while(1):
        _, frame = cap.read( )
        # flip the image
        img = cv2.flip(frame,1)
        wf, hf, _ = frame.shape
        hsv = cv2.cvtColor( frame ,cv2.COLOR_BGR2HSV ) #frame in hsv format
        lower_blue = np.array([95, 100, 50]) #lower hsv range of blue colour
        upper_blue = np.array([115, 255, 255]) #upper hsv range of blue colour
        img,mask,points = detect_inrange(frame,5000,500000, lower_blue, upper_blue)

        
        if len(points) != 0:
            x = points[0][0]
            y = points[0][1]
            rayon=points[0][2]
            frame = cv2.circle(frame,(x,y),rayon,(100,120,20),5)
            if(rayon > 10): #we draw bar if color detected with right size of circle
                img = cv2.rectangle( frame,(bar_start-largeur_paddle ,bar_lvl ), ( bar_start+largeur_paddle ,bar_lvl+hauteur_paddle ), ( 255 ,255 ,255 ), -1 )
                bar_start = int(x-largeur_paddle) #on update le mouvement du paddle
            else: 
                bar_start =wf//2
        else:
            img = cv2.rectangle( frame,(bar_start-largeur_paddle ,bar_lvl ), (bar_start+50 ,bar_lvl+hauteur_paddle ), ( 255 ,255 ,255 ), -1 )
        #on update le mouvement du ballon            
        x1 = x1 + dx
        y1 = y1 + dy
        y2 = y2 + dy
        x2 = x2 + dx
        #on dessine notre ballon
        img = cv2.circle(frame, ( x1 ,y1 ), 5, ( 255 ,255 ,255 ), -1)

        #on dessine les briques dans les coordonnées qu'on avait déja prédefini avant
        for i in range(4):
            for j in range(18):
                rec = bricks[i][j]
                if rec != []:
                    rec1 = str(rec)
                    rec_1 = rec1.split("_")
                    new_brick_x = int(rec_1[0])
                    new_brick_y = int(rec_1[1])
                img = cv2.rectangle( frame, ( new_brick_x , new_brick_y ), ( new_brick_x+50 , new_brick_y+10 ), ( 0 ,0+(10*j) ,0+(20*j) ), -1 )
        

        #si on percute une brique on l'enlève et on augmente le score
        for i in range(4):
            for j in range(18):
                ree = bricks[i][j]
                if ree != []:
                    deleted_brick = str(ree)
                    brick_coordinates = deleted_brick.split("_")
                    deleted_brick_x = int (brick_coordinates[0])
                    deleted_brick_y = int (brick_coordinates[1])
                    if (((deleted_brick_x <= x2 and deleted_brick_x+largeur_brick >=x2) or (deleted_brick_x <= x1 and deleted_brick_x+largeur_brick >=x1)) and y1<=deleted_brick_y ) or (y1<=largeur_brick):
                        dy = randint(1,5)
                        bricks[i][j]=[]
                        pts = pts+1
                        break               

        #on affiche le score
        msg = "Score : "+str(pts)
        font = cv2.FONT_HERSHEY_SIMPLEX
        bottomLeftCornerOfText = ( 230 ,25 )
        fontScale              = 1
        fontColor              = ( 0 ,0 ,0 )
        lineType               = 2

        #si le ballon percute les limites
        if ( x2 > 640 ):
            dx = -(randint(1, 5))
        if ( x1 <= 0 ):
            dx = randint(1,5)
        if ( y2 >= bar_lvl ):
            if (bar_start+largeur_paddle >= x2 and wf-( bar_start+largeur_paddle ) <= x2) or (bar_start+largeur_paddle >= x1 and bar_start <= x1):
                dy = -(randint(1, 5))
        if y2 >= bar_lvl:
            font = cv2.FONT_HERSHEY_SIMPLEX
            bottomLeftCornerOfText = ( 230 ,25 )
            fontScale              = 1
            fontColor              = ( 0 ,0 ,255 )
            lineType               = 2
            msg = 'Vous avez perdu.'       
            if y2 > bar_lvl+40:
                break
        cv2.putText( img ,msg,bottomLeftCornerOfText ,font ,fontScale ,fontColor ,lineType )
        #cv2.imshow( 'Mask' ,mask )
        cv2.imshow('frame',img)
        if cv2.waitKey(10)&0xFF==ord('q'):
            cap.release( )
            cv2.destroyAllWindows( )
            global no_stop
            no_stop = False
            break
while (no_stop):
    game( )