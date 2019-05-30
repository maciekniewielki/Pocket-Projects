import win32gui
import time
import random
import argparse
import win32api
import signal


class Wndw:
    def __init__(self, hwnd, starting_speed, rect, bounds):
        self.hwnd = hwnd
        self.starting_rect = rect
        self.left_x, self.top_y, self.right_x, self.bottom_y = rect
        self.width = self.right_x - self.left_x
        self.height = self.bottom_y - self.top_y
        self.speed_x, self.speed_y = starting_speed
        self.bounds = bounds

    @property
    def rect(self):
        return (self.left_x, self.top_y, self.right_x, self.bottom_y)

    def move_me(self, gravity):
        bounds = self.bounds
        self.speed_y += gravity
        if (self.right_x + self.speed_x >= bounds[2] and self.speed_x > 0) or (self.left_x - self.speed_x < bounds[0] and self.speed_x < 0):
            self.speed_x *= -1
        else:
            self.left_x += self.speed_x
            self.right_x += self.speed_x


        if (self.bottom_y + self.speed_y >= bounds[3] and self.speed_y > 0) or (self.top_y  - self.speed_y < bounds[1] and self.speed_y < 0):
            self.speed_y *= -1
        else:
            self.top_y += self.speed_y
            self.bottom_y += self.speed_y

        if not self.reset_if_outside():
            self.update_position()

    def update_position(self):
        win32gui.MoveWindow(self.hwnd, int(self.left_x), int(self.top_y), self.width, self.height, 1)

    def reset_if_outside(self):
        if outside(self.rect, self.bounds):
            self.reset_to_start()
            return True
        return False

    def reset_to_start(self):
        self.left_x, self.top_y, self.right_x, self.bottom_y = self.starting_rect
        self.update_position()



def outside(rect1, rect2):
    return rect1[2] < rect2[0] or rect1[0] > rect2[2] or rect1[1] > rect2[3] or rect1[3] < rect2[1]


def window_enumeration_handler(hwnd, top_windows):
    top_windows.append((hwnd, win32gui.GetWindowText(hwnd)))


def bounce_around(chosen_windows, gravity, fps):
    try:
        while True:
            if not chosen_windows:
                break
            for window in chosen_windows:
                window.move_me(gravity)
            time.sleep(1 / fps)
    except KeyboardInterrupt:
        for window in chosen_windows:
                window.reset_to_start()


def get_handles_from_names(names):
    current_window = win32gui.GetForegroundWindow()
    windows = []
    win32gui.EnumWindows(window_enumeration_handler, windows)
    chosen_windows = []
    for hwnd, window_name in windows:
        title = window_name.lower()
        for name in names:
            if name.lower() in title and hwnd != current_window:
                chosen_windows.append(hwnd)
                break
    return chosen_windows


def get_randomized_speed(min_speed, max_speed):
    speed_abs = min_speed + random.random() * (max_speed - min_speed)
    return speed_abs * random.choice([1, -1])


def init_window(hwnd, min_speed, max_speed):
    monitor_info = win32api.GetMonitorInfo(win32api.MonitorFromWindow(hwnd))
    speed_x = get_randomized_speed(min_speed, max_speed)
    speed_y = get_randomized_speed(min_speed, max_speed)
    window = Wndw(hwnd, (speed_x, speed_y), win32gui.GetWindowRect(hwnd),monitor_info["Work"])
    return window


def check_arguments(args):
    if args.min_speed > args.max_speed:
        print("Error: Minimum speed is higher than maximum")
        return False

    if args.min_speed < 0 or args.max_speed < 0:
        print("Error: Minimum or maximum speed is less than 0")
        return False

    if args.fps <= 0:
        print("Error: Fps is less than or equal to 0")
        return False

    return True


def parse_arguments():
    parser = argparse.ArgumentParser(description="Make the windows bounce around.")

    parser.add_argument("windows", type=str, help="Part of the window name that you wish to bounce (case insensitive). Can be more than one to affect multiple windows", nargs="+")
    parser.add_argument("-g", "--gravity", type=float, dest="gravity", default=0.0, help="Apply gravity with the specified strength (default: 0)")
    parser.add_argument("-min", "--min_speed", type=float, dest="min_speed", default=1.0, help="Minimum starting speed for the windows (default: 1)")
    parser.add_argument("-max", "--max_speed", type=float, dest="max_speed", default=6.0, help="Maximum starting speed for the windows (default: 6)")
    parser.add_argument("-fps", required=False, type=float, dest="fps", default=60, help="Number of updates per second (default: 60)")
    
    args = parser.parse_args()
    return args


def main():
    signal.signal(signal.SIGINT, signal.default_int_handler)

    args = parse_arguments()
    if not check_arguments(args):
        exit()

    window_handles = get_handles_from_names(args.windows)
    windows = [init_window(hwnd, args.min_speed, args.max_speed) for hwnd in window_handles]
    bounce_around(windows, args.gravity, args.fps)


if __name__ == "__main__":
    main()
