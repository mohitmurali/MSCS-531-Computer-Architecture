import matplotlib.pyplot as plt

# Pipeline stages and corresponding ticks for instruction [sn:1]
stages = ["Fetch", "Decode", "Execute", "Commit"]
ticks = [0, 79000, 79000, 86000]  # Timestamps from trace.out for [sn:1]

# Create the plot
plt.plot(ticks, range(len(stages)), marker='o', linestyle='-', color='b')
plt.yticks(range(len(stages)), stages)  # Set y-axis labels to pipeline stages
plt.xlabel("Ticks")                    # X-axis label
plt.ylabel("Pipeline Stage")           # Y-axis label
plt.title("Pipeline Progression for Instruction [sn:1] (XOR_R_R)")  # Plot title
plt.grid(True)                         # Add grid for readability
plt.tight_layout()                     # Adjust layout to fit labels

# Save the plot to a file instead of showing it
plt.savefig("pipeline_plot.png")
print("Plot saved as pipeline_plot.png")
