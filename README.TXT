Project: A Train Simulator Game for Kids
Group Members: Doruk Bildibay - 2237089
	       Hatice Aydın - 2236990
Folder Content:
	1. Assests for the simulation part, all .png format and 200*200 except the train.png
	2. trainLib.py: -The library created by us for the project based on the interface document.
		     	-It implements the requested methods for the Phase. 
		     	-The only libarary that we import is the *math* library.
	3. demo.py: -The demo code to use/visualize the functions of the trainLib.py module.
		    -To run: python demo.py
		    -To simulate the commands, we use the *pygame* module.
		    -For the command line, we import *cmd* and *sys* module.
		    -We import *time* module to sleep code somewhere.
		    -We also import *threading* module since we run display code as a thread.
		     Thanks to that, the user will be able to use comand line when the screen is 
		     still visible, and also he/she can examine the changes like adding element or
		     rotating a tile simultaneously.
	**Note: Since we use pygame to display grid, we banned the display() method not to print the grid
		into the terminal. It is still a valid function, but not to make terminal too busy we decided
		to exclude that. If it is requested, just a line of code will be sufficient.
	4.README.txt

Test Cases:
	- Defined in demo.py 
	- To run, just write the cammands as testcase1, testcase2 etc. Their conten will be explained below.
	  Also, using such as *help testcase1* command could be used for it.
	- Test cases generally creates different grids and shows the effects of the functions on that grid.
	  In case of you want to add some functions yourself after a testcase end for that grid, we dont
	  close the display window at the end of the testcases. If you want go through to another testcase directly, please
	  use *stopdisplay* command before hand.
	- To make the changes visible in the window/screen and the terminal, there are some *time.sleep(2)* commands in the
	  testcases. You can change them if you wish.
	- To make you understand what is going on, some prints are also located in the test cases, please also check the terminal
	  while the window/screen is displaying the cahnges.
	- Apart from these, of course you can run commands as you wish using the prompt. 
	
	testcase1: 
	testcase2:
	testcase3:
	testcase4:
	testcase5:
	testcase6:
	testcase7:
	testcase8:
	testcase9:
	testcase10: