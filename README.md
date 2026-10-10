## Ejecución de la aplicación

### 1. Crear ambiente virtual
```bash
python -m venv venv
```

### 2. Activar el Ambiente Virtual
**En Windows:**
```bash
source venv/Scripts/activate
```

**En Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Instalar las Dependencias
```bash
pip install -r requirements.txt
```

### 4. Iniciar aplicación
```bash
flask run --debug
```