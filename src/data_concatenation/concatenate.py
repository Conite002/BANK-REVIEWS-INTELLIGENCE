import os
import pandas as pd
from datetime import datetime

ROOT_DIR = os.path.expanduser('/data')

def build_macro_table(root_dir):
    # Initialize an empty Dataframe to hold all the data
    macro_df = pd.DataFrame()

    for date_dir in os.listdir(root_dir):
        date_path = os.path.join(root_dir, date_dir)
        if os.path.isdir(date_path):
            for  country_dir in os.listdir(date_path):
                country_path = os.path.join(date_path, country_dir)
                if os.path.isdir(country_path):
                    for city_dir in os.listdir(country_path):
                        city_path = os.path.join(country_path, city_dir)
                        if os.path.isdir(city_path):
                            for file in os.listdir(city_path):
                                if file.endswith('.parquet'):
                                    file_path = os.path.join(city_path, file)
                                    # Read the parquet file
                                    df = pd.read_parquet(file_path)
                                    df.head()
                                    # Print the number of rows in the Parquet file
                                    print(f"{file_path}: {len(df)} rows")
                                    

                                    # Add metadata columns
                                    df['date'] = date_dir
                                    df['country'] = country_dir
                                    df['city'] = city_dir

                                    macro_df = pd.concat([macro_df, df], ignore_index=True)

    # Create the macro_tables directory if it doesn't exist
    macro_tables_dir = os.path.join(os.path.dirname(os.getcwd()), "data", 'temp','macro_table')
    os.makedirs(macro_tables_dir, exist_ok=True)


    # Save the macro table as a Parquet file
    macro_table_parquet_path = os.path.join(macro_tables_dir, "macro_table.parquet")
    macro_df.to_parquet(macro_table_parquet_path, index=False)
    print(f"Macro table saved at: {macro_table_parquet_path}")

    macro_table_csv_path = os.path.join(macro_tables_dir, "macro_table.csv")
    macro_df.to_csv(macro_table_csv_path, index=False, encoding='utf-8')
    print(f"Macro table saved as CSV at : {macro_table_csv_path}")
    return macro_df
# build_macro_table(ROOT_DIR)



