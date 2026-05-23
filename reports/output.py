import pandas as pd
def export_report(
    report_df: pd.DataFrame,
    output_path: str = "outputs/traffic_summary.csv"
) -> None:
    

    if report_df.empty:
        print("Report is empty. Nothing to export.")
        return

    report_df.to_csv(output_path, index=False)

    print(f"Report exported successfully to: {output_path}")