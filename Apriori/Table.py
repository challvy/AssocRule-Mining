import matplotlib.pyplot as plt


if __name__ == "__main__":
    xx = [0.005,  0.006,  0.007,  0.008,  0.009,  0.010,  0.015,  0.020,  0.025,  0.030,  0.035,  0.040,  0.045,  0.050,  0.060,  0.070,  0.080,  0.090,  0.100]
    yy = [21.730, 21.800, 21.855, 21.900, 22.010, 22.230, 22.480, 22.309, 22.422, 21.977, 22.023, 21.953, 21.988, 21.930, 21.949, 21.949, 21.922, 21.941, 21.934]
    x  = [0.005,  0.006,  0.007,  0.008,  0.009,  0.010,  0.015,  0.020,  0.025,  0.030,  0.035,  0.040,  0.045,  0.050,  0.060,  0.070,  0.080,  0.090,  0.100]
    y  = [45.527, 44.363, 43.395, 50.402, 42.148, 42.691, 46.531, 44.023, 42.617, 39.820, 41.574, 42.453, 41.242, 36.605, 30.094, 30.215, 27.727, 25.496, 25.738]
    plt.figure(figsize=(8, 4))
    plt.ylim(20,55)
    plt.xlim(0.000, 0.100)
    plt.plot(x, y,  "b--", label="$FP-Growth$",linewidth=1)
    plt.plot(xx, yy, "r--", label="$Apriori$",linewidth=1)
    plt.xlabel("min_sup")
    plt.ylabel("Memory/MB")
    plt.title("Storage")
    plt.legend()
    plt.show()

