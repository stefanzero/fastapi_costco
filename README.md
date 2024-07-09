# fastAPI_costco

Data model for React foodcart app deployed to a FastAPI server

Products are organized by departments

example: Produce
https://costco.stefanzero.com/costco/departments/120/

Products are further organized by aisles

example: Vegetables
https://costco.stefanzero.com/costco/departments/120/aisles/677

Individual Products may also contain other products in these sections:
- Featured Products
- Related Items
- Often Bought With

example:
https://costco.stefanzero.com/costco/departments/116/aisles/732?item=11361739

## Installation

### Prerequisites
- Python
- Pipenv

### Setup

Create virtual environment and install packages in requirements.txt
```
pipenv install
```

## Run

```
uvicorn src.main:app --reload
```

## View testing web page

http://127.0.0.1:8000/docs

