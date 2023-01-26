import mediapipe as mp
from random import randint   
import cv2


mp_drawing = mp.solutions.drawing_utils #helps to render the landmarks
mp_hands = mp.solutions.hands

cap = cv2.VideoCapture(0)

#defining the ball & its steps
dx, dy = 4,4 #vitesse du ballon
x1,y1 = 90,150 #init top left
x2,y2 = 100,160 #init bottom right
offset_mvt = 50
bar_lvl = 400
bricks_start_x = 10
bricks_start_y = 50
largeur_brick = 60
hauteur_brick =20
pts=0
h = 640
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

with mp_hands.Hands(min_detection_confidence=0.5 , min_tracking_confidence=0.5) as hands:


    while cap.isOpened():

        re, frame = cap.read()

        # start the detection


        # convert the image to RGB
        image = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)

        # flip the image
        image = cv2.flip(image,1)

        image.flags.writeable = False

        # this is the main process
        results = hands.process(image)

        image.flags.writeable = True

        # print the results
        #print(results.multi_hand_landmarks)

        if results.multi_hand_landmarks:



            for handLMS in results.multi_hand_landmarks:

                for id , lm in enumerate(handLMS.landmark):
                    
                    # get the dimantions of the image
                    h , w , c = image.shape 

                    # get the X,Y of a finger
                    cx, cy = int(lm.x * w), int(lm.y * h)

                    # print the x,y of all the fingers 
                    # Each number = one finger and cx and cy are the position in the image 

                    #print (id , cx , cy)  

                    if id == 4 : # this is the thumb (pouce)
                        # lets draw a point 
                        cv2.circle(image , (cx,cy), 15 , (255,0,255), -1 )
                        thumbX = cx 
                        thumbY = cy
                        
                    if id == 8 : # this is the finger tip (index)
                        cv2.circle(image , (cx,cy), 15 , (255,0,255), -1 )   
                        fingerTipX = cx 
                        fingerTipY = cy
                        

                # Draw a line between the two fingers 
                cv2.line(image , (thumbX,thumbY), (fingerTipX,fingerTipY) , (0,0,255), 9)    
                
                #on update le mouvement du ballon            
                x1 = x1 + dx
                y1 = y1 + dy
                y2 = y2 + dy
                x2 = x2 + dx
                #on dessine notre ballon
                cv2.circle(image, (x1, y1), 7, ( 255 ,255 ,255 ), -1)

                #faire rebondir le ballon
                if(y2==thumbY or y2 ==fingerTipY) and (x1-20<thumbX<x2+20 or x1-20<fingerTipX<x2+20):
                    dy = -(randint(3, 5))

                #on dessine les briques dans les coordonnées qu'on avait déja prédefini avant
                for i in range(4):
                    for j in range(18):
                        rec = bricks[i][j]
                        if rec != []:
                            rec1 = str(rec)
                            rec_1 = rec1.split("_")
                            x12 = int(rec_1[0])
                            y12 = int(rec_1[1])
                        cv2.rectangle( image, ( x12 , y12 ), ( x12+50 , y12+10 ), ( 0 ,0+(10*j) ,0+(20*j) ), -1 )

                #si on percute une brique on l'enlève et on augmente le score
                for i in range(4):
                    for j in range(18):
                        ree = bricks[i][j]
                        if ree != []:
                            ree1 = str(ree)
                            ree_1 = ree1.split("_")
                            x13 = int (ree_1[0])
                            y13 = int (ree_1[1])
                            if (((x13 <= x2 and x13+50 >=x2) or (x13 <= x1 and x13+50 >=x1)) and y1<=y13 ) or (y1<=50):
                                dy = randint(1,5)
                                bricks[i][j]=[]
                                pts = pts+1
                                break 

                #on affiche le score
                msg = "SCORE : "+str(pts)
                font = cv2.FONT_HERSHEY_SIMPLEX
                bottomLeftCornerOfText = ( 230 ,25 )
                fontScale              = 1
                fontColor              = ( 0 ,0 ,0 )
                lineType               = 2

                #si le ballon percute les limites
                if ( x2 >= 640 ):
                    dx = -(randint(1, 5))
                if ( x1 <= 0 ):
                    dx = randint(1,5)
                if ( y2 >= bar_lvl ):
                    if((y2==thumbY or y2 ==fingerTipY)or (y1==thumbY or y1 ==fingerTipY)) and ((x1-20<thumbX<x2+20 or x1-20<fingerTipX<x2+20)or ((x1-20<thumbY<x2+20 or x1-20<fingerTipY<x2+20))):
                        dy = -(randint(3, 5))
                if y2 >= bar_lvl:
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    bottomLeftCornerOfText = ( 230 ,25 )
                    fontScale              = 1
                    fontColor              = ( 0 ,0 ,255 )
                    lineType               = 2
                    msg = 'Vous avez perdu.'       
                    if y2 > bar_lvl+40:
                        break
                cv2.putText( image ,msg,bottomLeftCornerOfText ,font ,fontScale ,fontColor ,lineType )
                
                    

        # recolor back the image to BGR
        image = cv2.cvtColor(image,cv2.COLOR_RGB2BGR)
        cv2.imshow('image',image)

        if cv2.waitKey(10) & 0xff == ord('q'):
            break



cap.release()
cv2.destroyAllWindows()