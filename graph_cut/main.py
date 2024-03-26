import sys, getopt
import cv2
import numpy as np
import matplotlib.pyplot as plt
from graph_cut import BoykovKolmorogov
from img_to_graph import img_to_graph

drawing = False
mode = "ob"
marked_ob_pixels=[]
marked_bg_pixels=[]
I=None
I_dummy=None


def mark_seeds(event,x,y,flags,param):
	global drawing,mode,marked_bg_pixels,marked_ob_pixels,I_dummy
	h,w,c=I_dummy.shape

	if event == cv2.EVENT_LBUTTONDOWN:
		drawing = True
	elif event == cv2.EVENT_MOUSEMOVE:
		if drawing == True:
			if mode == "ob":
				if(x>=0 and x<=w-1) and (y>0 and y<=h-1):
					marked_ob_pixels.append((y,x))
				cv2.line(I_dummy,(x-3,y),(x+3,y),(0,0,255))
			else:
				if(x>=0 and x<=w-1) and (y>0 and y<=h-1):
					marked_bg_pixels.append((y,x))
				cv2.line(I_dummy,(x-3,y),(x+3,y),(255,0,0))
	elif event == cv2.EVENT_LBUTTONUP:
		drawing = False
		if mode == "ob":
			cv2.line(I_dummy,(x-3,y),(x+3,y),(0,0,255))
		else:
			cv2.line(I_dummy,(x-3,y),(x+3,y),(255,0,0))


def main():
	global I,mode,I_dummy

	inputfile = ''
	try:
		opts, args = getopt.getopt(sys.argv[1:], "i:h", ["input-image=", "help"])
	except getopt.GetoptError:
		print('fast_seg.py -i <input image>')
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print ('fast_seg.py -i <input image>')
			sys.exit()
		elif opt in ("-i", "--input-image"):
			inputfile = arg
	print('Using image: ', inputfile)

	I=cv2.imread(inputfile) #imread wont rise exceptions by default
	I_dummy=np.zeros(I.shape)
	I_dummy=np.copy(I)

	cv2.namedWindow('Mark the object and background')
	cv2.setMouseCallback('Mark the object and background',mark_seeds)
	while(1):
		cv2.imshow('Mark the object and background',I_dummy)
		k = cv2.waitKey(1) & 0xFF
		if k == ord('o'):
			mode = "ob"
		elif k == ord('b'):
			mode = "bg"
		elif k == 27:
			break
	cv2.destroyAllWindows()
	

	G, s, t, I_marked, sp_lab = img_to_graph(I, marked_ob_pixels, marked_bg_pixels)
	G_residual = BoykovKolmorogov(G, s, t, capacity='sim').max_flow()
	
	h,w,c=I.shape
	St, _ = G_residual.graph['trees']
	partition = (set(St), set(G) - set(St))
	F=np.zeros((h,w),dtype=np.uint8)
	for sp in partition[0]:
		for pixels in sp.pixels:
			i,j=pixels
			F[i][j]=1
	Final=cv2.bitwise_and(I,I,mask = F)


	plt.subplot(2,2,1)
	plt.tick_params(labelcolor='black', top='off', bottom='off', left='off', right='off')
	plt.imshow(I[...,::-1])
	plt.axis("off")
	plt.xlabel("Input image")

	plt.subplot(2,2,2)
	plt.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
	plt.imshow(I_marked[...,::-1])
	plt.axis("off")
	plt.xlabel("Super-pixel boundaries and centroid")

	plt.subplot(2,2,3)
	plt.imshow(sp_lab)
	plt.axis("off")
	plt.xlabel("Super-pixel representation")


	plt.subplot(2,2,4)
	plt.imshow(Final[...,::-1])
	plt.axis("off")
	plt.xlabel("Output Image")

	
	cv2.imwrite("out.png",Final)
	plt.show()

if __name__ == '__main__':
	main()