from schedulers import EDF, LLF, RM

def main():
    simulator = RM()

    simulator.add_task("Ping", 20, 5, 8, 15)
    simulator.add_task("Pong", 35, 7, 14, 29)
    #simulator.add_task("Hack", 330, 9, 70, 80)

    simulator.run()

if __name__ == "__main__":
    main()