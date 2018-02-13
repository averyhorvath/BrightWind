SYNOPSIS
========

This script analyzes quantum Monte Carlo data to determine the ground-state equation of state of harmonically trapped many-fermion systems in two spatial dimensions. These are systems that are realized with ultracold atom experiments.

SETUP
=====

Requirements
------------
* `pip3 install -r requirments.txt`
    
    * run this command in terminal to install the required python modules*


MANY BODY
====
Number of particles that were measured ranged from N = 2 to N = 20 skipping by 2. Each pair possessed a bare value of 0.2, 1, 2, 3, 4, or 6.

* The CSV was sorted such that data with the same N value was organized together
* Each N data group was sorted by bare value
* The following nested for loop:
    `for key in sort.keys():`
        `data = sort[key]`
        `for bare in bare_space:`
        `sliced = data[data.bare==bare]`
        `group = sliced.groupby('beta_omega').mean()`
    can be translated as: for each key (N value), slice the data into dataframes for each bare value. For that specific N and bare value's dataframe, take the mean of all data for each beta_omega value in that data frame. This step takes the 10,000 line data frame and splices it into a 10-line dataframe for each N value. 
* The energy values (`<E>/Omg`) were plotted against the beta_omega value

* The error is then given by the `stderr(E)/Omg` values. The error bars are plotted on the graphs. 

* The energy values for each fixed bare and N value were seen to converge at beta_omega = 2.5. This was the expected result. 

TWO BODY
====
* The steps explained above were repeated for just the two-body case.

* Again, the energy values for each fixed bare and N value were seen to converge at beta_omega = 2.5. This was the expected result. 

TWO BODY VS. MANY BODY
====
* The plots generated used a fixed beta omega value of 2.5.
* The energy for the many body case was divided by the N value to represent it as a two body case. 
* Plots compared the energy for many body case represented as a two body case versus the energy two body case for a fixed beta omega value of 2.5 
* The green arrows on the plot represent the ideal case
