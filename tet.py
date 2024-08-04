import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation

# Parameters for the simulation
time_period = 0.02  # in seconds, shorter time period for better visualization
frequency = 294  # initial frequency in Hz for 3 L/min
sampling_rate = 10000  # samples per second
t = np.linspace(0, time_period, int(sampling_rate * time_period), endpoint=False)

fig, ax = plt.subplots(figsize=(12, 6))
fig.canvas.manager.set_window_title("Square Wave Simulation for YF-S401")
line, = ax.plot(t, np.zeros_like(t), label='Square Wave Signal')
ax.set_title('Square Wave Signal Simulating YF-S401 Output at 3 L/min (294 Hz)')
ax.set_xlabel('Time (seconds)')
ax.set_ylabel('Amplitude')
ax.grid(True)
ax.legend()
ax.set_ylim(-0.1, 1.1)

# Initialize the time counter
current_time = 0

# Function to update the data for the animation
def update(frame):
    global frequency, current_time
    # Update the frequency (you can add your logic to change frequency here)
    frequency += 1  # Example: increase the frequency by 1 Hz each frame
    if frequency > 300:
        frequency = 294  # Reset frequency after it reaches 300 Hz

    # Update the current time
    current_time += time_period

    # Generating square wave signal
    signal = 0.5 * (1 + np.sign(np.sin(2 * np.pi * frequency * t)))
    line.set_ydata(signal)
    line.set_xdata(t + current_time)

    ax.set_xlim(current_time, current_time + time_period)
    ax.set_title(f'Square Wave Signal Simulating YF-S401 Output at {frequency} Hz')
    return line,

# Create the animation
ani = animation.FuncAnimation(fig, update, frames=200, interval=50, blit=True)

plt.show()
