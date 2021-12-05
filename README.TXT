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
	**Note1: Since we use pygame to display grid, we banned the display() method not to print the grid
		into the terminal. It is still a valid function, but not to make terminal too busy we decided
		to exclude that. If it is requested, just a line of code will be sufficient.
	**Note2: trainLib.py and demo.py is created using Python v3.9.4
	**Note3: To install *pygame* module please run one of the following commands according to your environment:
			-Windows: py -m pip install -U pygame --user
			-Mac: python3 -m pip install -U pygame --user
			-Anaconda Mac: pythonw3 -m pip install -U pygame --user
			-Debian/Ubuntu/Mint: sudo apt-get install python3-pygame
			-Fedora/Red hat: sudo yum install python3-pygame
			-OpenSUSE: sudo zypper install python3-pygame
			-Arch/Manjaro: sudo pamac install python-pygame

	4.README.txt



Test Cases:
	- Defined in demo.py 
	- To run, just write the cammands as testcase1, testcase2 etc. Their conten will be explained below.
	  Also, using such as *help testcase1* command could be used for it.
	- Test cases generally creates different grids and shows the effects of the functions on that grid.
	  In case of you want to add some functions yourself after a testcase end for that grid, we dont
	  close the display window at the end of the testcases. If you want go through to another testcase 
	  directly, please use *stopdisplay* command before hand.
	- To make the changes visible in the window/screen and the terminal, there are some *time.sleep(2)* 
	  commands in the testcases. You can change them if you wish.
	- To make you understand what is going on, some prints are also located in the test cases, please also 
	  check the terminal while the window/screen is displaying the cahnges.
	- Apart from these, of course you can run commands as you wish using the prompt. 
	
	testcase1: It tries to create grids at different sizes, get error messages first, 
			   finally gives the right command and display grid.
	testcase2: Create a 4x4 grid and add each element type at some positions. 
	testcase3: Display remove functionality
	testcase4: Display rotation functionality
	testcase5: Displays the getduration & getstop functionality
	testcase6: Display nextcell & switchstate functionality 
	testcase7: Create a train at different cells
	testcase8: Display the advancetrain functionality , which moves the train, and print the status of the train
	testcase9: It contains some commands to crate a visual move
	