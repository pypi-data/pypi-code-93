import serial.tools.list_ports
print("starting")
ports = serial.tools.list_ports.comports()

for i in ports:
    print("******************************************************************************************")
    print(f"Description: {i.description}")
    print(f"Device: {i.device}")
    print(f"HWID: {i.hwid}")
    print(f"Interface: {i.interface}")
    print(f"Manufacturer: {i.manufacturer}")
    print(f"Name: {i.name}")
    print(f"PID: {i.pid}")
    print(f"Product: {i.product}")
    print(f"Serial Number: {i.serial_number}")
    print(f"VID: {i.vid}")

print(len(ports))
if len(ports) == 0:
    print("There are no devices connected to com ports.")
else:
    print("******************************************************************************************")