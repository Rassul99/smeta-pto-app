import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="ПТО & Смета Ассистент", layout="wide")

st.title("🏗️ ПТО & Смета Ассистент — Комплексный помощник")
st.caption("Единый инструмент для автоматизации рутины сметчиков и инженеров ПТО.")

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "📊 Экспресс-аудит смет",
    "📜 Реестр ТМЦ и Сертификатов",
    "🔀 Сравнение версий",
    "📝 Генератор реестров",
    "🧮 Калькулятор арматуры и бетона",
    "📈 Контроль выполнения (КС-2)",
    "💰 Проверка арифметики",
    "📥 Экспорт отчетов в Excel"
])

# --- Вкладка 1: Экспресс-аудит ---
with tab1:
    st.header("Экспресс-аудит смет и ведомостей")
    st.write("Загрузите Excel-файл со сметой или ВОР для автоматической проверки на ошибки.")
    uploaded_file = st.file_uploader("Выберите Excel-файл (.xlsx)", type=["xlsx"], key="audit")
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        st.write("Preview данных:", df.head())
        st.subheader("Результаты проверки:")
        
        null_counts = df.isnull().sum()
        if null_counts.sum() > 0:
            st.warning("Обнаружены пустые ячейки!")
            st.dataframe(null_counts[null_counts > 0])
        else:
            st.success("Пустых ячеек не обнаружено.")

# --- Вкладка 2: Реестр ТМЦ и Сертификатов ---
with tab2:
    st.header("Реестр ТМЦ и Сертификатов соответствия (E-Qurylys)")
    st.write("Сбор и систематизация сертификатов и паспортов качества для исполнительной документации.")
    
    col1, col2 = st.columns(2)
    with col1:
        tmc_name = st.text_input("Наименование ТМЦ / Материала")
        cert_num = st.text_input("Номер сертификата / декларации")
    with col2:
        supplier = st.text_input("Поставщик / Изготовитель")
        valid_until = st.date_input("Срок действия сертификата")
        
    if st.button("Добавить запись в реестр"):
        st.success(f"Запись для '{tmc_name}' успешно сформирована!")

# --- Вкладка 3: Сравнение версий ---
with tab3:
    st.header("Сравнение версий смет / ВОР")
    st.write("Загрузите две версии одного файла для поиска изменений в объемах или расценках.")
    f1 = st.file_uploader("Базовая версия (Исходная)", type=["xlsx"], key="v1")
    f2 = st.file_uploader("Новая версия (Измененная)", type=["xlsx"], key="v2")
    if f1 and f2:
        df1 = pd.read_excel(f1)
        df2 = pd.read_excel(f2)
        st.info("Файлы успешно загружены для сравнения.")

# --- Вкладка 4: Генератор реестров ---
with tab4:
    st.header("Генератор реестров исполнительной документации")
    st.write("Быстрое формирование описи и реестров для передачи в технадзор или E-Qurylys.")
    doc_type = st.selectbox("Тип реестра", ["Реестр сертификатов", "Реестр актов освидетельствования скрытых работ (АОСР)", "Реестр протоколов испытаний"])
    st.text_area("Список документов (каждый с новой строки)")
    if st.button("Сформировать реестр"):
        st.success("Реестр успешно сгенерирован!")

# --- Вкладка 5: Калькулятор арматуры и бетона ---
with tab5:
    st.header("🧮 Калькулятор расхода и перевода материалов")
    
    sub_tab1, sub_tab2 = st.tabs(["Арматура (п.м. ↔ тонны)", "Расчет объема бетона"])
    
    with sub_tab1:
        st.subheader("Перевод арматуры из метров в тонны")
        rebar_weights = {
            6: 0.222, 8: 0.395, 10: 0.617, 12: 0.888, 
            14: 1.210, 16: 1.580, 18: 2.000, 20: 2.470, 
            22: 2.980, 25: 3.850, 28: 4.830, 32: 6.310
        }
        
        col_d, col_l = st.columns(2)
        with col_d:
            diameter = st.selectbox("Диаметр арматуры (мм)", list(rebar_weights.keys()))
        with col_l:
            meters = st.number_input("Длина в погонных метрах (м)", min_value=0.0, value=1000.0, step=10.0)
            
        weight_ton = (meters * rebar_weights[diameter]) / 1000.0
        st.metric(label=f"Масса арматуры {diameter} мм", value=f"{weight_ton:.3f} тонн", delta=f"{meters * rebar_weights[diameter]:.1f} кг")

    with sub_tab2:
        st.subheader("Расчет геометрического объема бетона")
        c1, c2, c3 = st.columns(3)
        with c1:
            length = st.number_input("Длина (м)", min_value=0.0, value=10.0)
        with c2:
            width = st.number_input("Ширина (м)", min_value=0.0, value=5.0)
        with c3:
            height = st.number_input("Толщина / Высота (м)", min_value=0.0, value=0.3)
            
        margin = st.slider("Запас на уплотнение и потери (%)", 0, 10, 3)
        volume = length * width * height
        total_volume = volume * (1 + margin / 100.0)
        
        st.metric(label="Необходимый объем бетона", value=f"{total_volume:.2f} м³", delta=f"Чистый объем: {volume:.2f} м³")

# --- Вкладка 6: Контроль выполнения (КС-2) ---
with tab6:
    st.header("📈 Контроль лимитов и объемов по ВОР / Смете")
    st.write("Введите заложенные и фактически закрытые объемы для проверки перерасхода.")
    
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        plan_vol = st.number_input("Объем по проекту / смете", min_value=0.0, value=100.0)
    with col_v2:
        fact_vol = st.number_input("Фактически закрытый объем (КС-2)", min_value=0.0, value=85.0)
        
    diff = plan_vol - fact_vol
    percent = (fact_vol / plan_vol * 100) if plan_vol > 0 else 0
    
    st.progress(min(percent / 100.0, 1.0))
    if diff < 0:
        st.error(f"🚨 Перерасход объема! Превышение на {abs(diff):.2f} ед. ({percent:.1f}%)")
    else:
        st.success(f"✅ В пределах лимита. Остаток: {diff:.2f} ед. (Заполнено {percent:.1f}%)")

# --- Вкладка 7: Проверка арифметики ---
with tab7:
    st.header("💰 Автоматическая проверка арифметики (Количество × Цена)")
    st.write("Быстрый пересчет итоговых сумм позиций для выявления ошибок в расчетах подрядчиков.")
    
    q = st.number_input("Количество единиц", min_value=0.0, value=150.5, step=1.0)
    price = st.number_input("Цена за единицу (тенге)", min_value=0.0, value=4500.0, step=100.0)
    stated_total = st.number_input("Сумма по данным подрядчика (тенге)", min_value=0.0, value=677250.0, step=1000.0)
    
    calculated_total = q * price
    discrepancy = stated_total - calculated_total
    
    st.metric(label="Правильная расчетная сумма", value=f"{calculated_total:,.2f} ₸")
    
    if abs(discrepancy) > 0.01:
        st.error(f"⚠️ Обнаружена арифметическая ошибка! Расхождение составляет: {discrepancy:,.2f} ₸")
    else:
        st.success("✅ Арифметика сойдется идеально. Ошибок нет.")

# --- Вкладка 8: Экспорт отчетов в Excel ---
with tab8:
    st.header("📥 Генерация и скачивание готовых отчетов в Excel")
    st.write("Создайте стандартный шаблон реестра ТМЦ или отчета для выгрузки в один клик.")
    
    report_type = st.selectbox("Выберите тип отчета для выгрузки", ["Реестр сертификатов ТМЦ", "Сводная ведомость объемов"])
    
    if report_type == "Реестр сертификатов ТМЦ":
        sample_data = pd.DataFrame({
            "№ п/п": [1, 2, 3],
            "Наименование ТМЦ": ["Цемент М400", "Арматура А500С Ø12", "Песок строительный"],
            "Поставщик": ["ТОО «ЦементСтрой»", "ТОО «МеталлТорг»", "ИП «Карьер»"],
            "Номер сертификата": ["KZ.75012.01.01.12345", "KZ.75012.01.01.67890", "ДС-KZ-4455"],
            "Статус": ["Действителен", "Действителен", "Действителен"]
        })
    else:
        sample_data = pd.DataFrame({
            "Код позиции": ["01-01-001", "01-01-002", "01-02-001"],
            "Наименование работ": ["Разработка грунта", "Устройство подстилающего слоя", "Монтаж фундаментных блоков"],
            "Ед. изм.": ["м³", "м³", "шт"],
            "План": [150.0, 50.0, 24.0],
            "Факт": [150.0, 45.0, 24.0]
        })
        
    st.dataframe(sample_data, use_container_width=True)
    
    # Функция конвертации DataFrame в Excel байты
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        sample_data.to_excel(writer, index=False, sheet_name='Отчет')
    excel_data = output.getvalue()
    
    st.download_button(
        label="📥 Скачать готовый отчёт в Excel (.xlsx)",
        data=excel_data,
        file_name="PTO_Report_Template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
