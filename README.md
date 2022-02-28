## GTD analysis

### Dashboard

Code for dashboard lives in the dashboard.py

requirements.txt lists all the required dependencies.

### Run locally

Please note that program at the moment assumes that you create a pickle file manually from the main dataset.
Please note that this is quite a big file so I could not commit it into git.

I did that to have faster iteration time because normal xlsx file was very costly to read compared to pickle file.

```

import pandas as pd

GTD = pd.read_excel("Datasets/GTD_Dataset.xlsx")
GTD.to_pickle("Datasets/GTD_Dataset.pkl")

```


Once you have all the deps install you can run the dashboard using:

```bokeh serve --show dashboard.py```

It will open the dashboard in a browser window. Also hosted at: http://ec2-3-12-198-204.us-east-2.compute.amazonaws.com:8000/dashboard for convinience. (Currently it doesn't work)


### Analysis

I tried to analyse data mainly from three dimensions:


1. How terrorism shifted from one region to other over the years
2. How attack types and target types changed over the time
3. Economical impact of these attacks over the world.



### Thank you

Please feel free to reach me in case of any questions!

