import ScanUtility
import bluetooth._bluetooth as bluez
import math
import matplotlib.pylab as pylab

### Stage 2: Read RSSI
def scan_beacons(A,B,C):

    #Initialize variables for each beacon's RSSI
    rssi_a = 0
    rssi_b = 0
    rssi_c = 0

    i_a = 0
    i_b = 0
    i_c = 0
    
    #Store 10 RSSI values for each beacon
    while i_a < 10 or i_b < 10 or i_c < 10:
        returnedList = ScanUtility.parse_events(sock, 10)
        for item in returnedList:
            print(item)
            print("")
            if item["uuid"][0]=='a':
                rssi_a = item.get('rssi')
                if i_a<10:
                    A[i_a]=rssi_a
                    i_a = i_a+1
            elif item["uuid"][0]=='b':
                rssi_b = item.get('rssi')
                if i_b<10:
                    B[i_b]=rssi_b
                    i_b = i_b+1
            elif item["uuid"][0]=='c':
                rssi_c = item.get('rssi')
                if i_c<10:
                    C[i_c]=rssi_c
                    i_c = i_c+1
    return A,B,C

    
def localize(A,B,C,c,p,q,r,xr,yr):

    #Initialize constant for path loss
    n = 1.642
    
    #Initialize sums for moving average
    sumA = 0
    sumB = 0
    sumC = 0

### Stage 3: Convert RSSI to distance
    for i in range(10):
        if A[i] != 0:
            print("Distance of beacon A is: ")
            dis_a = round(10**((-A[i]+c)/(10*n)),3)
            print(dis_a)
            sumA = sumA + dis_a

        if B[i] != 0:
            print("Distance of beacon B is: ")
            dis_b = round(10**((-B[i]+c)/(10*n)),3)
            print(dis_b)
            sumB = sumB + dis_b

        if C[i] != 0:
            print("Distance of beacon C is: ")
            dis_c = round(10**((-C[i]+c)/(10*n)),3)
            print(dis_c)
            sumC = sumC + dis_c
        
### Stage 4: Trilateration with A(0,0), B(1,0), C(0,1)
        x = round((dis_a**2 - dis_b**2 + p**2)/(2*p),3)
        y = round(((dis_a**2 - dis_c**2 + q**2 + r**2)/(2*r)) - (q/r)*x,3)

        print ("The Raspberry is at ({},{})".format(x,y))
        
### Stage 5: Show Pi on map
        pylab.plot(0, 0, 'bs') #'bs' blue square
        pylab.plot(0, 1, 'bs') 
        pylab.plot(1, 0, 'bs') 
        pylab.plot(x, y, 'bs')
        
        #Error Calculation
        Error = round(math.sqrt((x-xr)**2+(y-yr)**2),3)
        print("Error = {}".format(Error))
        
    pylab.show()
    
    return sumA,sumB,sumC

#Initialize real coordinates (xr,yr)
xr = float(input("Enter measured x coordinate of Pi: "))
yr = float(input("Enter measured y coordinate of Pi: "))

#Set bluetooth device. Default 0.
dev_id = 0
try:
    sock = bluez.hci_open_dev(dev_id)
    print ("\n *** Looking for BLE Beacons ***\n")
    print ("\n *** CTRL-C to Cancel ***\n")
except:
    print ("Error accessing bluetooth")

#Initialize arrays for beacons
A = [0 for i in range(10)]
B = [0 for i in range(10)]
C = [0 for i in range(10)]

#Initialize constant for measured power of BLE
c = -62.81

#Initialize trilateration variables
p = 1
q = 0
r = 1

ScanUtility.hci_enable_le_scan(sock)

#Scans for iBeacons
try:
    A,B,C = scan_beacons(A,B,C)
except KeyboardInterrupt:
    pass

sumA,sumB,sumC = localize(A,B,C,c,p,q,r,xr,yr)

### Stage 6: Optimization

## Moving average
avrA = round(sumA/10,3)
print("The moving average of beacon A is: ")
print(avrA)

avrB = round(sumB/10,3)
print("The moving average of beacon B is: ")
print(avrB)

avrC = round(sumC/10,3)
print("The moving average of beacon C is: ")
print(avrC)

#New coordinates calculation
xo = round((avrA**2 - avrB**2 + p**2)/(2*p),3)
yo = round(((avrA**2 - avrC**2 + q**2 + r**2)/(2*r)) - (q/r)*xo,3)

print ("The Raspberry is at ({},{})".format(xo,yo))

#New error calculation
Error1 = round(math.sqrt((xo-xr)**2+(yo-yr)**2),3)
print("New error = {}".format(Error1))

## Constant c calculation
c = 0
c1 = 0
c2 = 0
c3 = 0

#Initialize known distance of each beacon
dis_a = 0.253
dis_b = 0.035
dis_c = 0.253

#Initialize RSSI values for each beacon
rssi_a = -53
rssi_b = -39
rssi_c = -53

#Calculate c
c1 = round(rssi_a + 10*math.log10(dis_a),3)
c2 = round(rssi_b + 10*math.log10(dis_b),3)
c3 = round(rssi_c + 10*math.log10(dis_c),3)

c = round((c1+c2+c3)/3,3)

#Calculate new error
try:
    A,B,C = scan_beacons(A,B,C)
except KeyboardInterrupt:
    pass

sumA,sumB,sumC = localize(A,B,C,c,p,q,r,xr,yr)
