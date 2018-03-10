# VersionML - Git for Data Science Projects

VersionML helps you manage and move around between iterations during model building.



## How versionml can help you?

We provide a git like command line tool for you to take a snapshot of your current state with all necessary information and dependent files.


## How to use it?


### Installation
	
```
pip install versionml
```


## Usage

## Initializing a versionml project. 

It will also initialize a new git repository, if one doesn't exist already.

```
versionml init
```

## Building your model with versionml

Continue with your model building. Say you are starting with `model.py`. Add versionml package to your code, like below.

```python

# model.py

import versionml

## your code goes here ##

## Add the below lines.

with versionml.state() as state:
	state.set( model=MODEL_OBJECT, params = { "PARAM_KEY_1" : "PARAM_VALUE_1" }, metrics = { "METRICS_KEY_1" : "METRICS_KEY_2" }, 
	remarks = "REMARKS" )

```

Note : Now run you can run model.py as usual with `python model.py`.


### Save your current state by passing a command line argument `save` to your model.py.

```
python model.py save
```

This takes a snapshot of all your files and along with other information. It will save the iteration with a unique id (Iteration Id).

```
# You will be seeing this line when you run `python model.py save`.

[VersionML] iteration id : <ITERATION_ID>
```

### List all saved iterations.

```
versionml ls
```

### Choose and commit a saved iteration.

This will add a permenant commit to your git. For the iteration id, try `versionml ls`.

```
versionml commit <ITERATION_ID>
```

### List all commited iterations.

```
versionml commit ls
```

### Reusing a commited iteration. 

```
versionml reuse <COMMITED_ITERATION_ID>
```

Note : `COMMITED_ITERATION_ID` is the iteration id from `versionml commit ls`.


### Stash the changes on your current workspace.

```
versionml stash
```

### Restore the stash.

```
versionml restore
```

### Loading a saved/commited iteration on your code for serving.

```python

import versionml

## For saved iterations `versionml ls` and commited iterations `versionml commit ls`.

model = versionml.load("<ITERATION_ID>")

## Your code.

```

## Happy Model Building :)



