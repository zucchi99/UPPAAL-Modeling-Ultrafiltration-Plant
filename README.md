# Hybrid Modeling, Simulation, and Sub-Optimal Synthesis of a controller for the Ultrafiltration of Industrial Wastewater
The aim of this work is to model, simulate and optimize an ultrafiltration process.
A detailed specification of how the experiments were conducted (and thus of the data collection) is available on this repository in the master's thesis of Francesco Zuccato (of which we report here its abstract).

## Thesis Abstract
Historically, many industries have required large amounts of fresh water for their processes. The typical
water cycle involves buying fresh water, using it in the process, and disposing of the wastewater without
recovery, necessitating a constant supply of new water. This pattern is known as *“take-make-dispose”*
and has always been the standard, according to the traditional economy. But nowadays, **water has become a scarce resource**.

The objective of this thesis is to exploit and adapt solid formal methods and tools developed in the
area of Computer Science with the aim of reducing the water footprint of industries, helping them in the
transition **towards a circular economy**. Ultrafiltration (UF) is an industrial process used to purify
liquids by filtering them through specialized membranes. In particular, UF is a crucial technology for
pretreating wastewater, enabling its reintroduction into the industrial process. With UF, is possible to
filter a large volume of wastewater, producing a small amount of solid waste and a significant amount
of reusable clean water.

In this thesis, we first examined formal tools for representing complex real systems, such as Timed
Automata (TA) and **Hybrid Automata (HA)**. Unfortunately, many problems with HA are well-known
to be undecidable. To analyze and verify properties of HA, we employed Statistical Model Checking
(SMC). SMC is a Monte Carlo-based method that allows to estimate system’s properties without requiring
a complete formal analysis.

Then, we develop a computational model to study, simulate, and **optimize an ultrafiltration process**. 
The model relies on Hybrid Automata, a formal object designed to describe complex systems
that exhibit both continuous and discrete behaviors in their dynamics. The model is composed of two
main components: one is the environment, in which ultrafiltration is simulated using ordinary differential
equations, and the other is the controller, which can alter the working conditions.

The hybrid automaton is implemented in **Uppaal**, a software tool for modeling, simulating, and
verifying real-time systems. Uppaal Stratego enables the **synthesis of sub-optimal controllers** based
on a given cost function. Utilizing SMC, Stratego explores a finite number of possible executions (finite
traces) to minimize a cost function, which in ultrafiltration is primarily energy consumption.

Finally, we present the experimental results, demonstrating that the model’s simulated data closely
estimates real data. Additionally, we show how various strategies can be defined and optimized, such as
minimizing total energy consumption for a cost-effective approach or minimizing total time for a faster
solution.

## Repository Structure
Folders:
* **app**: apart from the below explained sub-directories, the main folder contains the following files: 
   * ```main.py```: executes the entire data analysis (by typing ```python3 main.py```). Some parameters (such as the handling possible outliers) can be set with the the file ```parameters.json```. At the moment it is not possible to pass the parameters as arguments to the ```main.py``` file.
   *  ```parameters.json```: contains the parameters for the ```main.py``` file. Allows to customize some behaviours during the data analysis. Yet, the whole analysis has been tested only with the default parameters.
   * ```Dockerfile```: contains the docker instructions to build the docker image.
   * ```download_and_install_container.sh```: contains the shell instructions that automatically build the image and start the container.
   * ```TODO```: contains the set of next features to be implemented.
* **src**: contains python files and notebooks for the preliminary data analysis part and for the estimation of coefficient and parameters necessary to simulate the experiments in UPPAAL.
* **.docker**: contains the file ```requirements.txt```, which specifies the set of needed python packages, that can be automatically installed using docker.
* **output**: contains all the output files generated by the data analysis. Note that along the computation the data is elaborated and transformed, but is stored inside the ```data``` path not in the ```output``` path. The output path only stores the following sub-directories:
   * **notebooks_html**: contains the export of all the run notebooks. Note that the first notebooks are computed many times, one for each experiment setting. From the html files one can easily debug and check step-by-step the executed operations.
   * **estimated_coefficients**: contains the file ```estimated_coefficients.json``` which lists for each response variable $y$ the set of explanatory variables $x_1, ..., x_n$ with the corresponding coefficients $a_1, ..., a_n$ that allow the estimation of $y$ using a linear model of the $x$ variables: $y = a_1 * x_1 + .... + a_n * x_n$.
   * **images**: contains the charts exported from the notebooks.
* **data**: contains all the data necessary for the analysis. There are three sub-directories:
    * **concentrations**: containts an excel file manually hand-written containing the concentration levels used during the experiments (currently ignored by the pipeline)
    * **from_sensors**: contains the real data collected during the experiments. The data is so organized:
      * **0_raw/UF**: stores the raw csv data as exported from the machine
      * **1_extended**: stores the transformed data, again partitioned in:
         * **v1**: which splits each data raw file in multiple files, one per each concentration level (*). The data here stored is generated by the notebook ```0_extend__df_raw.ipynb```. Note that it is created also a file ```ALL_DATA.csv``` which merges all the files in ```v1``` together and thus contains all the available data. This file is useful for having a general view and for the exploratory data analysis part but in the end is not used.
         * **v2**: ideally the data here stored should be generated by the notebook ```3_add_concentrations.ipynb```, which should try to estimate and fill the gasps where the concentration levels are missing. Yet, it is still to be understood how to perform such operation, thus notebook ```3_add_concentrations.ipynb``` is skipped and this folder stays empty.
         * **v3**: here there is only output file ```estimated_parameters.csv``` which is generated by the notebook ```4_simulate_flux_ARIMA.ipynb```. Note that it is invoked multiple times: each concentration file is filtered processed as many times as the number of different level of transmembrane pressure (TMP) present. The notebook assumes the series of data comes from a unique concentration level and a unique TMP value. Then, using the ARIMA models tries to predict the series over time (this step is not necessary if each experimental settings already lasts more than 20-30 minutes).
    * **from_uppaal**: the data coming from the UPPAAL simulations.
      * **0_raw**: the raw data exported from UPPAAL (how to do so is later explained). Even though each simulations generates a single csv file but with a peculiar structure: teh columns are attached one to the other in vertical. Also, different columns can have different lenghts (the values of the continous variables are reported with a much higher frequency).
      * **1_repaired**: here each simulation is transormed to a dataframe with a classical structure. First is fixed a maximum frequency (0.01 minutes) and then all the columns are joined together.
      * **2_extended**: here the discrete columns are filled and the columns are renamed.

## Source Files - Data Analysis (Python)
The data analysis part is implemented in python, by a sequence of python notebooks.
The ```main.py``` file invokes the various notebooks. There are two additional python files: ```constants.py```, which imports all the needed packages and define set of costants used (such as paths) and the ```functions.py``` which contains the functions that are shared across the notebooks. The notebooks are the following:
* **0_extend__df_raw**: extends the raw data by adding derived columns (such as the flux, the resistance, the viscosity, etc.).
* **1_explore__df_ext**: has no real effect, it just serves for exploring the dataset and understand correlations and mutual effects.
* **2_estimate_factors**: the goal is to define simple models that allow to compute and estimate some observation variables. The estimated coefficients are then exported to the ```estimated_coefficients.json``` file (**).
* **3_add_concentrations**: as above said, is to be implemented yet.
* **4_simulate_flux_ARIMA**: generates simulation of the flux towards the future using the ARIMA models. Particularly relevant when the real data collected for a fixed setting spans over a small time interval.
* **5a_add_initial_flux**: is used to estimate the real value of the initial flux. Since the frequency at which data is gathered is 1 minute, there can be up to 1 minute of delay between the moment in which the pressure has been changed and the sensors record the data. So, the real initial flux $J_0$ is estimated using the precedent value of the resistance, the last one before the change of the pressure.
* **5b_estimate_flux_slope**: is used to estimated the flux slope, also referred to as $k_n$ in many papers, the constant rate at which the flux differential equation decreases: 
$$\dfrac{d J}{d t} = - k_n J^{2-n} (J - J_{min}) {\rm {with}} J \ge J_{min}$$. 
As visible, in the first iterations seems quickly decreasing and then it stabilizes (for  any of the four fouling mechanisms). Note that it stabilizes only when the flux is simulated using the ARIMA models, which may not be a true simulation. Moreover, even if the plots have a kind of logarithmic shape, no linear model has given a satisfactory p-value and R-squared. Thus, at the end, this notebook is useless, and we tried in UPPAAL different constant values, between $$5 * 10^{-6}$$ and $$6 * 10^{-6}$$, assuming that the fouling method is a cake filtration (and thus $n=0$).
* **5c_estimate_flux_min**: is used to estimate *a priori* the $J_{min}$, which is necessary to compute since the beginning the above differential equation. In order to so, we found two linear models: a simpler one, only based on the initial flux $J_0$; and a more complex one, based on the initial flux $J_0$, the transmembrane pressure $TMP$ and the initial total resistance $R_{tot}^0$.
The complex model achieves better results but is affected by a severe collinearity (VIF). Probably the reason for the high VIF is also due to the limited dataset we had, because all the factors make sense mechanistically.
* **6_estimate_flux**: this is a validation notebook: it compute the flux over time by using the estimated initial flux $J_{0}$, the estimated minimum flux $J_{min}$. Note that the differential equation is approximated using a discretazion of time.
* **7_load_uppaal_series**: transforms the raw simulated data exported from UPPAAL into a dataframe that can be easily justaxposed on the real data to validate the UPPAAL simulations. Of course, the UPPAAL simulations must be adjusted in order to alter the pressure in the same way as was done during the experiments.
* **8_compare_estimated_vs_uppaal**: finally the final validation of the model is possible: a chart is built by justaxposing the real data with the UPPAAL's simulations. Also, the error metrics are computed, for example: ```R-squared=0.9936```, ```MAPE=3.08%```.

## Compilation
1. clone the repository: ```git clone https://github.com/zucchi99/UPPAAL-Modeling-Ultrafiltration-Plant.git```
1. if missing, install docker: ```apt-get install docker-compose```
1. run the script ```download_and_install_container.sh``` which will download and install the image and then will start the container.
1. copy your raw data files to analyze in the path ```data/0_raw/UF```
1. launch the pipeline ```python3 main.py```

At the end in the folder ```/app/output/``` will find the generated images, the estimated coefficients, and the html version of all the notebooks launched with any parameter.

## Output Example
To see an example of the pipeline's output without pulling the repository you can check the folder ```/example-outcome/```.
To avoid data duplication on GitHub, the folder ```/example-outcome/data/``` does contain the raw data, which is already available in the ```/data/``` folder.

## Conduct your own data analysis
TODO.

## UPPAAL Model
TODO.
