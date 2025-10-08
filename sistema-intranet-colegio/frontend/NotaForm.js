// NotaForm.js
import React, { useState } from 'react';

const NotaForm = () => {
    const [estudianteId, setEstudianteId] = useState('');
    const [cursoId, setCursoId] = useState('');
    const [nota, setNota] = useState('');

    const handleSubmit = async(e) => {
        e.preventDefault();

        const nuevaNota = { estudianteId, cursoId, nota };

        try {
            const response = await fetch('http://localhost:5000/api/notas', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(nuevaNota),
            });

            const data = await response.json();
            console.log(data.message);
            alert(data.message);
        } catch (error) {
            console.error('Error al registrar la nota:', error);
            alert('Hubo un error al registrar la nota.');
        }
    };

    return ( <
        form onSubmit = { handleSubmit } >
        <
        h2 > Registrar Nueva Nota < /h2> <
        label >
        ID de Estudiante:
        <
        input type = "text"
        value = { estudianteId }
        onChange = {
            (e) => setEstudianteId(e.target.value)
        }
        required / >
        <
        /label> <
        label >
        ID de Curso:
        <
        input type = "text"
        value = { cursoId }
        onChange = {
            (e) => setCursoId(e.target.value)
        }
        required / >
        <
        /label> <
        label >
        Nota:
        <
        input type = "number"
        value = { nota }
        onChange = {
            (e) => setNota(e.target.value)
        }
        required / >
        <
        /label> <
        button type = "submit" > Guardar Nota < /button> < /
        form >
    );
};

export default NotaForm;