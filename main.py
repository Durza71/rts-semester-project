from schedulers import EDF, LLF, RM

def main():
    rm_control = RM(1000, "rm_control")
    llf_control = LLF(1000, "llf_control")
    edf_control = EDF(1000, "edf_control")

    rm_resource_limiting = RM(1000, "rm_limiting", True)
    llf_resource_limiting = RM(1000, "llf_limiting", True)
    edf_resource_limiting = RM(1000, "edf_limiting", True)

    rm_overruns = RM(1000, "rm_overruns")
    rm_overruns.add_overruns(250, 10, 20)
    llf_overruns = RM(1000, "llf_overruns")
    llf_overruns.add_overruns(250, 10, 20)
    edf_overruns = RM(1000, "edf_overruns")
    edf_overruns.add_overruns(250, 10, 20)

    simulations = [rm_control, llf_control, edf_control,
                   rm_resource_limiting, llf_resource_limiting, edf_resource_limiting,
                   rm_overruns, llf_overruns, edf_overruns]
    
    for simulation in simulations:
        simulation.add_task("Task_1", 20, 5, 4, 15)
        simulation.add_task("Task_2", 35, 7, 9, 29)
        simulation.add_task("Task_3", 71, 19, 13, 43)

        simulation.run()

if __name__ == "__main__":
    main()