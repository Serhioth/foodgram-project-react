import os
from pathlib import Path

import dotenv
import psycopg2
from fpdf import FPDF

dotenv.load_dotenv()


def make_pdf(ingredient_amount_list, spacing=1):
    """Function, what creates pdf-file from sql-data"""
    pdf = FPDF()
    pdf.add_font(
        'ofont.ru_Geologica',
        style='',
        fname=Path('recipes/fonts/ofont.ru_Geologica.ttf').resolve(),
        uni=True
    )
    pdf.add_page()
    pdf.set_font('ofont.ru_Geologica', size=12)

    data = [['Ингредиент', 'Количество', 'Ед. изм.']]
    data.extend(ingredient_amount_list)

    col_width = pdf.w / 4.5
    row_height = pdf.font_size

    for row in data:
        for item in row:
            pdf.cell(
                col_width,
                row_height * spacing,
                txt=item,
                border=1
            )
        pdf.ln(row_height*spacing)

    return pdf.output(dest='S').encode('latin-1')


def get_shopping_list(user_id):
    """Function, what returns data from db"""
    ingredient_amount_list = []

    conn = psycopg2.connect(
        database=os.getenv('POSTGRES_DB', 'django'),
        user=os.getenv('POSTGRES_USER', 'django'),
        password=os.getenv('POSTGRES_PASSWORD', ''),
        host=os.getenv('DB_HOST', ''),
        port=os.getenv('DB_PORT', 5432)
    )
    cur = conn.cursor()

    sql_query = f"""
        SELECT recipes_ingredient.name,
        CAST(SUM(recipes_ingredientamount.amount) AS CHAR(10))
        AS formatted_decimal,
        recipes_ingredient.measurement_unit
        FROM recipes_shoppingcart
        JOIN recipes_ingredientamount
        ON recipes_ingredientamount.recipe_id
        = recipes_shoppingcart.shopping_cart_recipes_id
        JOIN recipes_ingredient
        ON recipes_ingredientamount.ingredient_id = recipes_ingredient.id
        WHERE recipes_shoppingcart.user_id={user_id}
        GROUP BY recipes_ingredient.name, recipes_ingredient.measurement_unit;
    """

    cur.execute(sql_query)

    rows = cur.fetchall()

    for row in rows:
        ingredient_amount_list.append(row)

    cur.close()
    conn.close()
    return ingredient_amount_list
