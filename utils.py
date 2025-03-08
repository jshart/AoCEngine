# Useful utility function to regex match and/all numbers in a line
# handy for quick and dirty parsing of the input data
def extract_numbers(s):
    return [int(num) for num in re.findall(r'-?\d+', s)]

def decimalToAlphabeticLabel(n):
    if n == 0:
        return "A"
    
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    result = []
    
    while n > 0:
        n, remainder = divmod(n, 26)
        result.append(alphabet[remainder])
    
    return ''.join(reversed(result))

def lerp(value, in_min, in_max, out_min, out_max):
    # Calculate the mapped value
    inRange=in_max-in_min
    outRange=out_max-out_min
    if inRange==0:
        return 0
    return (value - in_min) * outRange / inRange + out_min

def calcAngle(a, b):
    x1,y1=a
    x2,y2=b
    # Calculate the differences
    delta_x = x2 - x1
    delta_y = y2 - y1

    # Calculate the angle in radians
    angle_rad = math.atan2(delta_y, delta_x)

    # Convert to degrees
    angle_deg = math.degrees(angle_rad)

    # Adjust to make "up" (north) as 0 degrees
    angle_from_north = (angle_deg + 90) % 360

    #print(f"The angle of point B from point A, with 'up' as 0 degrees, is {angle_from_north} degrees.")

    return angle_from_north

def calcDist(a,b):
    x1, y1 = a
    x2, y2 = b

    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return distance

def checkVisible(base, asteroids):
    consolidated_data = {}

    for a in asteroids:
        if a!=base:
            angle=calcAngle(base,a)
            distance=calcDist(base,a)
            #print("dist:",distance," at angle:",angle)
            if angle in consolidated_data:
                consolidated_data[angle].append((distance,a[0],a[1]))
            else:
                consolidated_data[angle] = [(distance,a[0],a[1])]

    return consolidated_data

def asciiDigitsList(inputString):
    retList = [ord(c) for c in inputString]
    retList.append(ord("\n"))
    return retList
