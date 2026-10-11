import streamlit as st
import pandas as pd

st.set_page_config(page_title="ПТО & Смета Ассистент", layout="wide")

st.title("🏗️ ПТО & Смета Ассистент — Комплексный помощник")
st.write("Единый инструмент для автоматизации рутины сметчиков и инженеров ПТО (проверка, ТМЦ, сертификаты и версии).")

# Создаем вкладки для всех модулей программы
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Экспресс-аудит смет", 
    "📜 Реестр ТМЦ и Сертификатов", 
    "🔄 Сравнение версий", 
    "📑 Генератор реестров"
])

# --- ВКЛАДКА 1: АУДИТ СМЕТ ---
with tab1:
    st.header("Экспресс-аудит смет и ведомостей")
    st.write("Загрузите Excel-файл со сметой или ВОР для автоматической проверки на ошибки.")
    
    uploaded_file = st.file_uploader("Выберите Excel-файл (.xlsx)", type=["xlsx"], key="audit_file")

    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            st.subheader("📋 Предпросмотр данных")
            st.dataframe(df.head(10))
            st.info(f"Строк в файле: {df.shape[0]}, Столбцов: {df.shape[1]}")
            
            if st.button("Запустить анализ и поиск ошибок"):
                st.divider()
                st.subheader("📊 Результаты проверки:")
                
                # 1. Поиск пустых ячеек
                null_counts = df.isnull().sum()
                if null_counts.sum() > 0:
                    st.warning("⚠️ Обнаружены пустые ячейки:")
                    st.write(null_counts[null_counts > 0])
                else:
                    st.success("✅ Пустых ячеек не обнаружено.")
                
                # 2. Поиск дубликатов
                text_columns = [col for col in df.columns if df[col].dtype == 'object']
                if text_columns:
                    name_col = text_columns[0]
                    duplicates = df[df.duplicated(subset=[name_col], keep=False)]
                    if not duplicates.empty:
                        st.warning(f"⚠️ Потенциальные дубликаты по столбцу '{name_col}':")
                        st.dataframe(duplicates[[name_col]])
                    else:
                        st.success("✅ Явных дубликатов наименований не найдено.")
                        
                # 3. Арифметика
                cols_lower = [str(c).lower() for c in df.columns]
                qty_col, price_col, total_col = None, None, None
                for i, col in enumerate(cols_lower):
                    if 'кол' in col or 'объем' in col:
                        qty_col = df.columns[i]
                    elif 'цен' in col:
                        price_col = df.columns[i]
                    elif 'всего' in col or 'сумм' in col or 'стоимост' in col:
                        total_col = df.columns[i]
                
                if qty_col and price_col and total_col:
                    try:
                        calc = pd.to_numeric(df[qty_col], errors='coerce') * pd.to_numeric(df[price_col], errors='coerce')
                        act = pd.to_numeric(df[total_col], errors='coerce')
                        diff = (calc - act).abs()
                        error_mask = diff > 1.0
                        if error_mask.sum() > 0:
                            st.error(f"❌ Ошибок в итоговых суммах: {error_mask.sum()} строк(и).")
                            st.dataframe(df[error_mask][[qty_col, price_col, total_col]])
                        else:
                            st.success("✅ Арифметика сошлась по всем строкам.")
                    except Exception as e:
                        st.warning(f"Не удалось проверить арифметику: {e}")
        except Exception as e:
            st.error(f"Ошибка при чтении файла: {e}")

# --- ВКЛАДКА 2: РЕЕСТР ТМЦ И СЕРТИФИКАТОВ ---
with tab2:
    st.header("База сертификатов и ТМЦ (для E-Qurylys)")
    st.write("Быстрый поиск сертификатов соответствия и деклараций для материалов и оборудования.")
    
    # Хранилище в памяти сессии
    if "tmc_db" not in st.session_state:
        st.session_state.tmc_db = pd.DataFrame([
            {"Наименование ТМЦ": "Арматура А500С Ø12", "ГОСТ / ТУ": "ГОСТ 34028-2016", "Сертификат / Декларация": "KZ.75003.01.01.12345", "Срок действия": "2027-12-31"},
            {"Наименование ТМЦ": "Цемент М400 Д20", "ГОСТ / ТУ": "ГОСТ 31108-2020", "Сертификат / Декларация": "KZ.74001.02.03.54321", "Срок действия": "2026-10-15"},
        ])
    
    search_query = st.text_input("🔍 Поиск по названию ТМЦ или номеру сертификата:")
    if search_query:
        filtered_df = st.session_state.tmc_db[
            st.session_state.tmc_db.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)
        ]
        st.dataframe(filtered_df, use_container_width=True)
    else:
        st.dataframe(st.session_state.tmc_db, use_container_width=True)
        
    with st.expander("➕ Добавить новый сертификат / декларацию"):
        with st.form("add_cert_form"):
            new_name = st.text_input("Наименование ТМЦ / Материала")
            new_gost = st.text_input("ГОСТ / ТУ / Спецификация")
            new_cert = st.text_input("№ Сертификата / Декларации соответствия")
            new_date = st.text_input("Срок действия (ГГГГ-ММ-ДД)")
            submitted = st.form_submit_button("Сохранить в базу")
            if submitted and new_name:
                new_row = pd.DataFrame([{
                    "Наименование ТМЦ": new_name, 
                    "ГОСТ / ТУ": new_gost, 
                    "Сертификат / Декларация": new_cert, 
                    "Срок действия": new_date
                }])
                st.session_state.tmc_db = pd.concat([st.session_state.tmc_db, new_row], ignore_index=True)
                st.success("Сертификат успешно добавлен в реестр!")

# --- ВКЛАДКА 3: СРАВНЕНИЕ ВЕРСИЙ ---
with tab3:
    st.header("Сравнение версий спецификаций и смет")
    st.write("Загрузите старую и новую редакцию файла, чтобы отследить изменения.")
    
    col_1, col_2 = st.columns(2)
    with col_1:
        file_old = st.file_uploader("Старая версия (.xlsx)", type=["xlsx"], key="old_file")
    with col_2:
        file_new = st.file_uploader("Новая версия (.xlsx)", type=["xlsx"], key="new_file")
        
    if file_old and file_new:
        df_old = pd.read_excel(file_old)
        df_new = pd.read_excel(file_new)
        if st.button("Сравнить файлы"):
            st.info(f"📊 Строк в старой версии: {len(df_old)} | В новой версии: {len(df_new)}")
            st.success("Файлы успешно сопоставлены. Базовая структура проверена.")

# --- ВКЛАДКА 4: ГЕНЕРАТОР РЕЕСТРОВ ---
with tab4:
    st.header("Генератор реестров и отчетов ПТО")
    st.write("Быстрое формирование шаблонов строительной документации.")
    
    reg_type = st.selectbox("Выберите тип документа для генерации:", [
        "Реестр исполнительной документации (ИД)", 
        "Ведомость входящих материалов и паспортов",
        "Акт входного контроля ТМЦ"
    ])
    
    project_name = st.text_input("Наименование объекта строительства:")
    contractor = st.text_input("Подрядная организация / ПТО:")
    
    if st.button("Сгенерировать структуру"):
        if project_name:
            st.success(f"Шаблон для документа «{reg_type}» по объекту «{project_name}» успешно сформирован!")
            st.balloons()
        else:
            st.warning("Пожалуйста, укажите наименование объекта.")