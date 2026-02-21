import os
import psycopg2
from flask import Flask, render_template, request, make_response
from flask import Flask, render_template, request, make_response, redirect
from dotenv import load_dotenv
from flask import flash


load_dotenv()

app = Flask(__name__)
app.secret_key = "supersecretkey"
DATABASE_URL = os.environ.get("DATABASE_URL")


def get_db_connection():
    return psycopg2.connect(DATABASE_URL)


@app.route("/")
def list_catches():
    page = int(request.args.get("page", 1))
    search = request.args.get("search", "")
    sort = request.args.get("sort", "date_desc")

    # Page size logic (cookie persistence)
    page_size_param = request.args.get("page_size")

    if page_size_param:
        page_size = int(page_size_param)
    else:
        page_size = int(request.cookies.get("page_size", 10))

    offset = (page - 1) * page_size

    base_query = """
        SELECT * FROM catches
        WHERE species ILIKE %s OR location ILIKE %s
    """

    order_clause = "ORDER BY catch_date DESC"

    if sort == "date_asc":
        order_clause = "ORDER BY catch_date ASC"
    elif sort == "species":
        order_clause = "ORDER BY species ASC"
    elif sort == "weight_desc":
        order_clause = "ORDER BY weight_lbs DESC NULLS LAST"

    final_query = f"""
        {base_query}
        {order_clause}
        LIMIT %s OFFSET %s
    """

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        final_query,
        (f"%{search}%", f"%{search}%", page_size, offset),
    )

    catches = cur.fetchall()

    cur.execute("SELECT COALESCE(AVG(weight_lbs), 0) FROM catches")
    avg_weight = cur.fetchone()[0]

    cur.execute("SELECT COALESCE(MAX(weight_lbs), 0) FROM catches")
    max_weight = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM catches;")
    total_records = cur.fetchone()[0]

    # Clean formatting
    avg_weight = round(float(avg_weight), 2)
    max_weight = float(max_weight)

    cur.close()
    conn.close()

    response = make_response(render_template(
        "list.html",
        catches=catches,
        page=page,
        page_size=page_size,
        total_records=total_records,
        search=search,
        sort=sort,
    ))

    # Store page size in cookie for 30 days
    response.set_cookie("page_size", str(page_size), max_age=30 * 24 * 60 * 60)

    return response

@app.route("/stats")
def stats():
    page_size = int(request.cookies.get("page_size", 10))

    conn = get_db_connection()
    cur = conn.cursor()

    # Total records
    cur.execute("SELECT COUNT(*) FROM catches;")
    total_records = cur.fetchone()[0]

    # Most common species
    cur.execute("""
        SELECT species, COUNT(*)
        FROM catches
        GROUP BY species
        ORDER BY COUNT(*) DESC
        LIMIT 1;
    """)
    most_common = cur.fetchone()
    if most_common is None:
        most_common = ("N/A", 0)

    # Average weight (safe)
    cur.execute("""
        SELECT COALESCE(ROUND(AVG(weight_lbs), 2), 0)
        FROM catches;
    """)
    avg_weight = cur.fetchone()[0]

    # Biggest fish (heaviest first, then longest)
    cur.execute("""
        SELECT species, weight_lbs, length_in, catch_date, image_url
        FROM catches
        WHERE weight_lbs IS NOT NULL OR length_in IS NOT NULL
        ORDER BY
            COALESCE(weight_lbs, 0) DESC,
            COALESCE(length_in, 0) DESC
        LIMIT 1;
    """)
    biggest_fish = cur.fetchone()  # can be None if table is empty

    cur.close()
    conn.close()

    return render_template(
        "stats.html",
        total_records=total_records,
        page_size=page_size,
        most_common=most_common,
        avg_weight=avg_weight,
        biggest_fish=biggest_fish
    )

@app.route("/new", methods=["GET", "POST"])
def add_catch():
    if request.method == "POST":
        species = request.form["species"]
        location = request.form["location"]
        catch_date = request.form["catch_date"]
        weight = request.form.get("weight_lbs") or None
        length = request.form.get("length_in") or None
        notes = request.form.get("notes")
        image_url = request.form["image_url"]

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO catches (species, location, catch_date, weight_lbs, length_in, notes, image_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (species, location, catch_date, weight, length, notes, image_url))

        conn.commit()
        cur.close()
        conn.close()

        flash("Catch added successfully!")

        return redirect("/")

    return render_template("form.html", catch=None)

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_catch(id):
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == "POST":
        species = request.form["species"]
        location = request.form["location"]
        catch_date = request.form["catch_date"]
        weight = request.form.get("weight_lbs") or None
        length = request.form.get("length_in") or None
        notes = request.form.get("notes")
        image_url = request.form["image_url"]

        cur.execute("""
            UPDATE catches
            SET species=%s,
                location=%s,
                catch_date=%s,
                weight_lbs=%s,
                length_in=%s,
                notes=%s,
                image_url=%s,
                updated_at=CURRENT_TIMESTAMP
            WHERE id=%s
        """, (species, location, catch_date, weight, length, notes, image_url, id))

        conn.commit()
        cur.close()
        conn.close()

        flash("Catch updated successfully!")

        return redirect("/")

    # GET request → load existing record
    cur.execute("SELECT * FROM catches WHERE id=%s;", (id,))
    catch = cur.fetchone()

    cur.close()
    conn.close()

    return render_template("form.html", catch=catch)

@app.route("/delete/<int:id>", methods=["GET", "POST"])
def delete_catch(id):
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == "POST":
        cur.execute("DELETE FROM catches WHERE id=%s;", (id,))
        conn.commit()
        cur.close()
        conn.close()

        flash("Catch removed successfully!")

        return redirect("/")

    # GET request → show confirmation page
    cur.execute("SELECT species FROM catches WHERE id=%s;", (id,))
    catch = cur.fetchone()

    cur.close()
    conn.close()

    return render_template("confirm_delete.html", catch=catch, id=id)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)