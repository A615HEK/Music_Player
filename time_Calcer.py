import re
# exit_flag = False
class Time_Values:
    def __init__(self, time_value:str|int = "0"):
        self.set_time(str(time_value))
        # print(f"Self: {self.time_in_secs()}")
    def __repr__(self):
        if self.time_day:
            return f"{self.time_day} : {self.time_hour} : {self.time_min} : {self.time_sec}"
        if self.time_hour:
            return f"{self.time_hour} : {self.time_min} : {self.time_sec}"
        else:
            return f"{self.time_min} : {self.time_sec}"
    def set_time(self, time_string:str = "0"):
        self.time_val = list(map(int, re.split('[- :.]', time_string)))
        self.time_val.reverse()
        self.time_val.extend([0]*(4-len(self.time_val)))
        self.time_val.reverse()
        self.time_day, self.time_hour, self.time_min, self.time_sec = self.time_val
        self.correction_time_overflow()
        self.time_val = f"DD : Hour : Min : Sec -> {self.time_day} : {self.time_hour} : {self.time_min} : {self.time_sec}"
    def time_in_secs(self) -> int:
        return (self.time_day*86400) + (self.time_hour*3600) + (self.time_min*60) + (self.time_sec)
    def correction_time_overflow(self):
        # Seconds correction
        self.time_min += self.time_sec // 60
        self.time_sec %= 60
        # Minutes correction
        self.time_hour += self.time_min // 60
        self.time_min %= 60
        # Hours correction
        self.time_day += self.time_hour // 24
        self.time_hour %= 24
    def correction_time_underflow(self):
        # Hour underflow
        self.time_day -= 1
        self.time_hour += 24
        # Minute underflow
        self.time_hour -= 1
        self.time_min += 60
        # Second underflow
        self.time_min -= 1
        self.time_sec += 60
    def add_time(self, other_time):
        # Seconds
        self.time_sec += other_time.time_sec
        # Minutes
        self.time_min += other_time.time_min
        # Hours
        self.time_hour += other_time.time_hour
        # Days
        self.time_day += other_time.time_day
        # Time correction
        self.correction_time_overflow()
    def sub_time(self, other_time):
        print(f"Self : {self.time_in_secs()}; Other : {other_time.time_in_secs()}")
        if self.time_in_secs() < other_time.time_in_secs():
            print("Warning: Time underflow. Operation not possible")
        else:
            # Days
            self.time_day -= other_time.time_day
            # Hours
            self.time_hour -= other_time.time_hour
            # Minutes
            self.time_min -= other_time.time_min
            # Seconds
            self.time_sec -= other_time.time_sec
            print(f"Within subtraction portion: {self}")
            # Time correction
            self.correction_time_underflow()
            self.correction_time_overflow()
# base_time_val = Time_Values()
# print(base_time_val)
# print("Time processor:\n*Operations supported for DD:HH:MM:SS or DD.HH.MM.SS")
# while not exit_flag:
#     # TODO: Include try catch block for wrongs
#     op_val = int(input("What do you want to do: 1. Add\t2.Subtract:\t"))
#     if op_val not in (1, 2):
#         exit_flag = True
#         break
#     input_time_val = Time_Values(input("Time to process: "))
#     print("Time entered: ",input_time_val)
#     # Add time
#     if op_val == 1:
#         base_time_val.add_time(input_time_val)
#     # Subtract time
#     if op_val == 2:
#         base_time_val.sub_time(input_time_val)
#     print(base_time_val)