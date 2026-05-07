import os
import argparse
import pandas as pd
import matplotlib.pyplot as plt


def load_and_prepare_data(csv_file, bucket_size):
    """
    Load CSV and prepare derived columns.
    """

    df = pd.read_csv(csv_file)

    df["Release Time"] = pd.to_numeric(df["Release Time"])
    df["Completion Time"] = pd.to_numeric(df["Completion Time"])
    df["Slack"] = pd.to_numeric(df["Slack"])

    # Tardiness
    df["Tardiness"] = df["Slack"].apply(lambda x: max(0, -x))

    # Time buckets
    df["Time Bucket"] = (
        (df["Completion Time"] // bucket_size) * bucket_size
    )

    return df


def generate_single_file_plots(csv_file, bucket_size=100):
    """
    Original mode:
    Generate plots grouped by task for a single CSV.
    """

    df = load_and_prepare_data(csv_file, bucket_size)

    base_name = os.path.splitext(os.path.basename(csv_file))[0]

    # -------------------------------------------------
    # Average Slack Over Time by Task
    # -------------------------------------------------
    slack_by_task = (
        df.groupby(["Time Bucket", "Task Name"])["Slack"]
        .mean()
        .reset_index()
    )

    plt.figure(figsize=(10, 6))

    for task in slack_by_task["Task Name"].unique():
        task_data = slack_by_task[
            slack_by_task["Task Name"] == task
        ]

        plt.plot(
            task_data["Time Bucket"],
            task_data["Slack"],
            marker="o",
            label=task
        )

    plt.xlabel("Time Bucket")
    plt.ylabel("Average Slack")
    plt.title("Average Slack Over Time by Task")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(f"{base_name}_average_slack_over_time.png")
    plt.close()

    # -------------------------------------------------
    # Average Tardiness Over Time by Task
    # -------------------------------------------------
    tardiness_by_task = (
        df.groupby(["Time Bucket", "Task Name"])["Tardiness"]
        .mean()
        .reset_index()
    )

    plt.figure(figsize=(10, 6))

    for task in tardiness_by_task["Task Name"].unique():
        task_data = tardiness_by_task[
            tardiness_by_task["Task Name"] == task
        ]

        plt.plot(
            task_data["Time Bucket"],
            task_data["Tardiness"],
            marker="o",
            label=task
        )

    plt.xlabel("Time Bucket")
    plt.ylabel("Average Tardiness")
    plt.title("Average Tardiness Over Time by Task")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(f"{base_name}_average_tardiness_over_time.png")
    plt.close()

    # -------------------------------------------------
    # Deadline Success Rate by Task
    # -------------------------------------------------
    deadline_rate = (
        df.groupby("Task Name")["Met Deadline"]
        .mean() * 100
    )

    plt.figure(figsize=(8, 5))

    deadline_rate.plot(kind="bar")

    plt.xlabel("Task")
    plt.ylabel("Percent Deadlines Met")
    plt.title("Deadline Success Rate by Task")
    plt.ylim(0, 100)
    plt.tight_layout()

    plt.savefig(f"{base_name}_deadline_success_rate_by_task.png")
    plt.close()

    print(f"Finished processing {csv_file}")


def compare_csv_files(csv_files, bucket_size=100):
    """
    Compare multiple CSV files together.
    Combines all task data into single metrics.
    """

    # -------------------------------------------------
    # Average Slack Comparison
    # -------------------------------------------------
    plt.figure(figsize=(10, 6))

    for csv_file in csv_files:

        df = load_and_prepare_data(csv_file, bucket_size)

        base_name = os.path.splitext(
            os.path.basename(csv_file)
        )[0]

        slack_over_time = (
            df.groupby("Time Bucket")["Slack"]
            .mean()
            .reset_index()
        )

        plt.plot(
            slack_over_time["Time Bucket"],
            slack_over_time["Slack"],
            marker="o",
            label=base_name
        )

    plt.xlabel("Time Bucket")
    plt.ylabel("Average Slack")
    plt.ylim(min(0, min(slack_over_time["Slack"] * 1.1)), max(slack_over_time["Slack"]) * 1.2)
    plt.title("Average Slack Comparison")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.savefig("comparison_average_slack.png")
    plt.close()

    # -------------------------------------------------
    # Average Tardiness Comparison
    # -------------------------------------------------
    plt.figure(figsize=(10, 6))

    for csv_file in csv_files:

        df = load_and_prepare_data(csv_file, bucket_size)

        base_name = os.path.splitext(
            os.path.basename(csv_file)
        )[0]

        tardiness_over_time = (
            df.groupby("Time Bucket")["Tardiness"]
            .mean()
            .reset_index()
        )

        plt.plot(
            tardiness_over_time["Time Bucket"],
            tardiness_over_time["Tardiness"],
            marker="o",
            label=base_name
        )

    plt.xlabel("Time Bucket")
    plt.ylabel("Average Tardiness")
    plt.ylim(min(0, min(tardiness_over_time["Tardiness"] * 1.1)), max(tardiness_over_time["Tardiness"]) * 1.2)
    plt.title("Average Tardiness Comparison")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.savefig("comparison_average_tardiness.png")
    plt.close()

    # -------------------------------------------------
    # Deadline Success Comparison
    # -------------------------------------------------
    labels = []
    values = []

    for csv_file in csv_files:

        df = load_and_prepare_data(csv_file, bucket_size)

        base_name = os.path.splitext(
            os.path.basename(csv_file)
        )[0]

        deadline_rate = (
            df["Met Deadline"].mean() * 100
        )

        labels.append(base_name)
        values.append(deadline_rate)

    plt.figure(figsize=(8, 5))

    plt.bar(labels, values)

    plt.xlabel("Dataset")
    plt.ylabel("Percent Deadlines Met")
    plt.title("Deadline Success Comparison")
    plt.ylim(0, 100)
    plt.tight_layout()

    plt.savefig("comparison_deadline_success.png")
    plt.close()

    print("Finished comparison plots")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Generate scheduling analysis plots."
    )

    parser.add_argument(
        "csv_files",
        nargs="+",
        help="CSV files to analyze"
    )

    parser.add_argument(
        "--bucket-size",
        type=int,
        default=200,
        help="Time bucket size"
    )

    parser.add_argument(
        "--compare",
        action="store_true",
        help="Compare multiple CSV files together"
    )

    args = parser.parse_args()

    # ---------------------------------------------
    # Compare mode
    # ---------------------------------------------
    if args.compare:

        if len(args.csv_files) < 2:
            parser.error(
                "--compare requires at least 2 CSV files"
            )

        compare_csv_files(
            args.csv_files,
            args.bucket_size
        )

    # ---------------------------------------------
    # Single-file mode
    # ---------------------------------------------
    else:

        for csv_file in args.csv_files:
            generate_single_file_plots(
                csv_file,
                args.bucket_size
            )