.RECIPEPREFIX = >
install:
> pip install -r requirements.txt
data:
> python build_data.py --years 2015 2024
run:
> streamlit run app.py
