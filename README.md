# GitML - Git for Data Science Projects

GitML helps you manage and move around between iterations during model building.



## How gitml can help you?

We provide a git like command line tool for you to take a snapshot of your current state with all necessary information and dependent files.


## How to use it?


### Installation
	
```
pip install gitml
```


## Usage

## Initializing a gitml project. 

It will also initialize a new git repository, if one doesn't exist already.

```
gitml init
```

## Building your model with gitml

Continue with your model building. Say you are starting with `model.py`. Add gitml package to your code, like below.

```python

# model.py

import gitml

## your code goes here ##

## Add the below lines.

with gitml.state() as state:
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

[GitML] iteration id : <ITERATION_ID>
```

### List all saved iterations.

```
gitml ls
```

### Choose and commit a saved iteration.

This will add a permenant commit to your git. For the iteration id, try `gitml ls`.

```
gitml commit <ITERATION_ID>
```

### List all commited iterations.

```
gitml commit ls
```

### Reusing a commited iteration. 

```
gitml reuse <COMMITED_ITERATION_ID>
```

Note : `COMMITED_ITERATION_ID` is the iteration id from `gitml commit ls`.


### Stash the changes on your current workspace.

```
gitml stash
```

### Restore the stash.

```
gitml restore
```

### Loading a saved/commited iteration on your code for serving.

```python

import gitml

## For saved iterations `gitml ls` and commited iterations `gitml commit ls`.

model = gitml.load("<ITERATION_ID>")

## Your code.

```

## Happy Model Building :)



