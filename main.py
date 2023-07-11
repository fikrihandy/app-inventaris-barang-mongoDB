import datetime
import pandas as pd
import streamlit as st
import pymongo

st.set_page_config(layout="wide")


def init_connection():
    return pymongo.MongoClient(**st.secrets["mongo"])


client = init_connection()


def get_data():
    db = client.barang
    items_collection = db.barang.find()
    items_hashable = list(items_collection)
    return items_hashable


def insert_data(document):
    db = client.barang
    result = db.barang.insert_one(document)
    if result.inserted_id:
        st.experimental_rerun()


def update_data(myquery, new_values):
    db = client.barang
    db.barang.update_one({"_id": myquery}, new_values)
    st.experimental_rerun()


def delete_data(id_dihapus):
    db = client.barang
    db.barang.delete_one({"_id": id_dihapus})
    st.experimental_rerun()


menu = ["Daftar Barang", "Tambah Baru", "Edit / Delete", "Tentang"]
tab1, tab2, tab3, tab4 = st.tabs(menu)

with tab1:
    st.header(menu[0])
    items = get_data()
    df = pd.DataFrame(items, index=range(1, len(items) + 1))
    df.drop('_id', axis=1, inplace=True)
    st.table(df)

with tab2:
    st.header(menu[1])
    with st.form('form_barang', clear_on_submit=True):
        nama = st.text_input('Nama Barang')
        deskripsi = st.text_area('Deskripsi Barang')
        jumlah = st.number_input('Jumlah Barang', min_value=0, value=1, step=1)
        kondisi = st.radio("Kondisi Barang", ('Rusak', 'Baik'), index=1)
        lokasi = st.text_input('Lokasi / Penempatan Barang')
        tanggal_pembelian = st.date_input('Tanggal Pembelian', value=datetime.date.today())
        tanggal_input = st.text_input(f'Tanggal Input', disabled=True, value=datetime.date.today())

        submitted = st.form_submit_button("Simpan")
        if submitted:
            doc = {
                "nama": nama,
                "deskripsi": deskripsi,
                "jumlah": jumlah,
                "kondisi": kondisi,
                "lokasi": lokasi,
                "tanggal_input": datetime.date.today().isoformat(),
                "tanggal_pembelian": tanggal_pembelian.isoformat()
            }
            insert_data(doc)

with tab3:
    st.header(menu[2])
    items = get_data()

    tuple_data = [(item["nama"], item["_id"]) for item in items]
    formatted_tuples = [f"{nama} - {id}" for nama, id in tuple_data]
    formatted_tuples.insert(0, "No data")

    option = st.selectbox(
        'Pilih barang (mongodump) yang akan di-edit / hapus',
        formatted_tuples)

    if option == "No data":
        st.warning("Silahkan memilih barang (mongodump) yang akan dilakukan pengeditan / penghapusan")

    for item in items:
        if str(item['_id']) == option.split()[-1]:
            with st.form("edit_delete_form"):
                st.text_input('ID:', item['_id'], disabled=True)
                nama = st.text_input('Nama Barang', value=item["nama"])
                deskripsi = st.text_area('Deskripsi Barang', value=item["deskripsi"])
                jumlah = st.number_input('Jumlah Barang', min_value=0, value=item["jumlah"], step=1)
                if item["kondisi"] == 'Baik':
                    lihat_kondisi = 1
                elif item["kondisi"] == 'Rusak':
                    lihat_kondisi = 0
                kondisi = st.radio("Kondisi Barang", ('Rusak', 'Baik'), index=lihat_kondisi)
                lokasi = st.text_input('Lokasi / Penempatan Barang', value=item["lokasi"])
                tanggal_pembelian = st.text_input('Tanggal Pembelian', disabled=True, value=item["tanggal_pembelian"])
                tanggal_input = st.text_input(f'Tanggal Input', disabled=True, value=item["tanggal_input"])

                col1, col2 = st.columns([0.1, 0.9], gap="small")
                with col1:
                    update = st.form_submit_button("Update Barang")
                    if update:
                        st.balloons()
                        updated = {"$set": {
                            "nama": nama,
                            "deskripsi": deskripsi,
                            "jumlah": jumlah,
                            "kondisi": kondisi,
                            "lokasi": lokasi,
                            "tanggal_input": item["tanggal_input"],
                            "tanggal_pembelian": item["tanggal_pembelian"]
                        }}
                        update_data(item["_id"], updated)
                        st.experimental_rerun()
                with col2:
                    delete = st.form_submit_button(f"Hapus {item['nama']}")
                    if delete:
                        delete_data(item["_id"])
with tab4:
    st.header(menu[3])
    st.balloons()

    col1, col2 = st.columns([0.3, 0.7], gap="small")
    with col1:
        st.json({
            "nama": "ABDULLAH FIKRI HANDI SAPUTRA",
            "nim": 215611098,
            "prodi": "Sistem Informasi (K1)",
            "thn_angkatan": 2021
        })
    with col2:
        st.subheader("Aplikasi ini dibuat sebagai bagian dari tugas UAS dalam mata kuliah Teknologi Basis Data.")
        st.divider()
        st.write("Aplikasi ini dikembangkan dengan menggunakan bahasa pemrograman Python dan framework Streamlit, "
                 "yang memungkinkan pembuatan antarmuka pengguna interaktif dan responsif.")
        st.divider()
        st.write("Untuk manajemen basis data, aplikasi ini menggunakan MongoDB, yang digunakan untuk menyimpan dan "
                 "mengelola data dalam sistem basis data.")
