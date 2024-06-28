
# TODO ENTIRELY
import sys
sys.path.insert(0, 'src')
from functions import *

params = DEFAULT_PARAMETERS

notebooks = [
    '0_extend__df_raw', 
    '1_explore__df_ext', 
    '2_estimate_factors', 
    #'3_add_concentrations', 
    '4_simulate_flux_ARIMA', 
    '5a_estimate_flux_slope', 
    '5b_estimate_flux_min', 
    '6_estimate_flux'
]

input_data_path = {
    '0_extend__df_raw' :        PATH_SENSORS_DATA_RAW_UF,
    '1_explore__df_ext' :       PATH_SENSORS_DATA_EXT_UF_V1,
    '2_estimate_factors' :      PATH_SENSORS_DATA_EXT_UF_V1,
    '4_simulate_flux_ARIMA':    PATH_SENSORS_DATA_EXT_UF_V1,
    '5a_estimate_flux_slope':   PATH_SENSORS_DATA_EXT_UF_V3,
    '5b_estimate_flux_min':     PATH_SENSORS_DATA_EXT_UF_V3,
    '6_estimate_flux':          PATH_SENSORS_DATA_EXT_UF_V3,
}

def merge_data_files() :
    df_all = pd.DataFrame()
    i = 0
    output_file = 'ALL_DATA.csv'
    output_file_path = f"{PATH_SENSORS_DATA_EXT_UF_V1}/{output_file}"
    for f in os.listdir(PATH_SENSORS_DATA_EXT_UF_V1) :
        if re.match('.*\.csv', f) and (not f in [output_file]) : 
            # read file
            f = PATH_SENSORS_DATA_EXT_UF_V1 + '/' + f
            df_cur = pd.read_csv(f)
            # drop outliers
            if drop_initial_final_off_rows :
                df_cur = drop_initial_final_rows(df_cur, log=False)
                df_cur, _ = get_df_ON_OFF(df_cur)
            if drop_off_rows :
                args = { 'log' : False }
                if drop_outliers :
                    df_cur, _ = remove_outliers(df_cur, cols=['res tot [1/m]'],    drop_fun=drop_outliers_far_median, args=args)
                    df_cur, _ = remove_outliers(df_cur, cols=['prs feed_2 [kPa]'], drop_fun=drop_outliers_far_neighbours, args=args)
                    df_cur, _ = remove_outliers(df_cur, cols=['flux [L/m^2h]'],    drop_fun=drop_outliers_out_range, args=args)
                    df_cur, _ = remove_outliers(df_cur, cols=['flux [L/m^2h]'],    drop_fun=drop_initial_jumps, args=args)
            # concatenate
            df_cur['file_idx'] = i
            #df_cur.loc[len(df_cur)] = empty_separator_row
            df_all = pd.concat([df_all, df_cur])
            i += 1
    df_all = df_all.drop('index', axis=1).reset_index(drop=True)
    # update tmp groups
    new_group = 0
    df_all.loc[0, 'new group'] = new_group
    for i in range(1, len(df_all)) :
        file_cur = df_all.loc[i, 'file_idx']
        file_prv = df_all.loc[i-1, 'file_idx']
        group_cur = df_all.loc[i, 'TMP group']
        group_prv = df_all.loc[i-1, 'TMP group']
        new_group += (1 if ((file_cur != file_prv) or (group_cur != group_prv)) else 0)
        df_all.loc[i, 'new group'] = new_group
        #print(f'files: {file_prv} -> {file_cur}, group: {group_prv} -> {group_cur}, new_group:{new_group}')
    df_all = df_all.drop('TMP group', axis=1).rename(columns={'new group' : 'TMP group'})
    # write to file
    df_all.to_csv(output_file_path, index=False)

def update_parameters_json(args=DEFAULT_PARAMETERS) :
    with open(PATH_FILE_PARAMETERS, 'w') as fid:
        json.dump(args, fid, indent=2)

def run_all() : 
    j = 1
    for notebook in notebooks :
        f_ipynb = f'src/{notebook}.ipynb'
        print(f"-------------------------------------- STEP: {j}, notebook: {f_ipynb}")
        data_path = input_data_path.get(notebook, None)
        file_idx = 0
        path_html = f'{PATH_NOTEBOOK_OUTPUT}/{notebook}'
        os.makedirs(path_html, exist_ok=True)
        # one execution per file
        for f_input in os.listdir(data_path) :
            f_html = f'{path_html}/{f_input}-{file_idx}.html'
            print(f"------------- STEP: {j}.{file_idx}\ninput data path: {data_path}\ninput data file: {f_input}\noutput notebook file: {f_html}")
            params['file_idx'] = file_idx
            # one execution per file and per tmp
            if notebook in ['4_simulate_flux_ARIMA'] :
                if f_input != 'ALL_DATA.csv' :
                    tmps_idxs = TMP_INTERVALS[f_input]
                    print(tmps_idxs)
                    k = 0
                    for (tmp_idx, _) in tmps_idxs.items() :
                        f_html_2 = re.sub("\.html$", f"-{k}.html", f_html)
                        print(f"-------- STEP: {j}.{file_idx}.{k}, tmp index: {k}, input data path: {data_path}, input data file: {f_input}, output notebook file: {f_html}")
                        params['tmp_idx'] = tmp_idx
                        update_parameters_json(params)
                        run_notebook(f_ipynb, f_html_2)
                        k += 1
            else :
                update_parameters_json(params)
                run_notebook(f_ipynb, f_html)
            file_idx += 1
        if notebook == '0_extend__df_raw' :
            merge_data_files()
        j += 1

def run_notebook(notebook_file, output_file):
    """Pass arguments to a Jupyter notebook, run it and convert to html."""
    # Run the notebook
    subprocess.call([
        'jupyter-nbconvert',
        '--execute',
        '--to', 'html',
        '--output', output_file,
        notebook_file
    ])


def read_from_json(json_file, key) : 
    with open(json_file, 'r') as f:
        data = json.load(f)
    return data[key]

#############################
# MAIN

# reset parameters with default values
update_parameters_json()

# read parameters
params = read_parameters()

# set local parameters
drop_outliers = params['drop_outliers']
drop_initial_final_off_rows = params['drop_initial_final_off_rows']
drop_off_rows = params['drop_off_rows']

# set notebook global parameters
params['plot_scatterplot_matrix'] = True

# run pipeline
run_all()
# merge_data_files()

# reset parameters with default values
update_parameters_json()