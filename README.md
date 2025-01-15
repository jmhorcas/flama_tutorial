# Tutorial: how to use flamapy from Python scripts

### Download and install
1. Install [Python 3.9+](https://www.python.org/)
2. Clone this repository and enter into the main directory:

    `git clone https://github.com/jmhorcas/flama_tutorial`

3. Create a virtual environment: 

    `python -m venv env`

4. Activate the environment: 

    `. env/bin/activate` (in Linux)
    
    `.\env\Scripts\Activate` (in Windows)

5. Install flamapy and plugins:

    `pip install flamapy` (this install flamapy including all the available plugins)

    or alternatively:

    `pip install flamapy-fw flamapy-fm flamapy-sat flamapy-bdd` (this install only the framework and the desired plugins)

6. Run the tutorial.py:

    `python tutorial.py`
