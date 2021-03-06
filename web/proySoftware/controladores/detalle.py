#!/usr/bin/env python
# -*- coding: utf-8 -*-
from proySoftware import app
from flask import render_template
from flask_wtf import FlaskForm
from wtforms import Form, StringField, IntegerField, validators
from flask import request
from flask import redirect
from flask import url_for
from flask import make_response
from flask import flash
from flask import session
from wtforms.validators import *


from ..models import *
from ..utils import *

#formulario para analisis
class AnalisisForm(Form):
		analisis = StringField('analisis')
		comentario = StringField('comentario')
		puntuacion = IntegerField('puntuacion', validators=[NumberRange(min=0, max=10)])

#class ComentarioForm(Form):
#		comentario = StringField('comentario')


@app.route('/<name>/<int:pk>/', methods=['GET'])
def details(name, pk):
		'''
		Router: solo accesible mediante el método GET de HTTP/HTTPS.
		Descripción: details hace una petición get de Videojuego que satisfaga
		id = pk recuperada de la url
		'''
		videojuego = Videojuego.query.get(pk)
		cover = get_videogame_cover(pk)
		score = puntnMedia(pk)
		analisForm = AnalisisForm()
		plataformas = Plataforma.query.filter(
			PlataformaVideojuego.id_videojuego == pk, PlataformaVideojuego.id_plataforma == Plataforma.id).all()
		desarrolladora = Desarrolladora.query.filter(
			DesarrolladoraVideojuego.id_videojuego == pk, DesarrolladoraVideojuego.id_desarrolladora == Desarrolladora.id).all()
		generos = Genero.query.filter(
			GeneroVideojuego.id_videojuego == pk, GeneroVideojuego.id_genero == Genero.id).all()
		#comentForm = ComentarioForm()
		
		listAnalis = get_analisis(pk)
		if 'nick' in session:
			jug_des = UsuarioVideojuego.query.filter(UsuarioVideojuego.id_usuario == get_user_id(), UsuarioVideojuego.id_videojuego == pk).first()
		else:
			jug_des = []
		if listAnalis:
			for analisis in listAnalis:
					id_user = analisis.id_usuario
					user_nick = get_user_name(id_user)
					analisis.user = user_nick
					listcoment = get_comentario(analisis.id)
					analisis.coments = listcoment
		return render_template('_views/detalles.html',
            videojuego=videojuego,
            cover=cover,
            score=score,
						analisForm=analisForm, listAnalis=listAnalis, 
						plataformas=plataformas, desarrolladora = desarrolladora,
						generos = generos, jug_des=jug_des)



def comentar(name, pk):
		#cargar info de los formularios
		formulario = AnalisisForm(request.form)
		if 'nick' in session:
			texto = formulario.data['comentario']
			if len(texto) < 500 :
				#obtener datos
				id = get_user_id()
				
				#crear nuevo analisis en bd
				insertar_comentario(id, pk, texto)
				flash('Enviado', 'success')
				response = make_response(redirect(url_for('details', name=name, pk=get_videogame_id(name))))
			else:
				flash('Demasiado largo', 'danger')
				response = make_response(redirect(url_for('details', name=name, pk=get_videogame_id(name))))
		else :
			flash('Login requerido', 'danger')
			response = make_response(redirect(url_for('details', name=name, pk=pk)))
		return response
	
def puntuar(name, pk):
		#cargar info de los formularios
		formulario = AnalisisForm(request.form)
		if 'nick' in session:
			#obtener datos
			id = get_user_id()
			texto = formulario.data['puntuacion']
			if formulario.validate() :
				#crear nuevo analisis en bd
				insertar_puntuacion(id, pk, texto)
				flash('Enviado', 'success')
				response = make_response(redirect(url_for('details', name=name, pk=pk)))
			else :
				flash('Datos no validos', 'danger')
				response = make_response(redirect(url_for('details', name=name, pk=pk)))
		else :
			flash('Login requerido', 'danger')
			response = make_response(redirect(url_for('details', name=name, pk=pk)))
		return response
	
@app.route('/<name>/<int:pk>/', methods=['POST'])
def detalles(name, pk):
		#cargar info de los formularios
		formulario = AnalisisForm(request.form)
		if 'nick' in session:
			#obtener datos
			id = get_user_id()
			texto = formulario.data['analisis']
			if texto == '':
				texto = formulario.data['comentario']
				if texto == '':
					response = puntuar(name, pk)
				else :
					response = comentar(name, pk)
			else :
				if len(texto) < 1000 :
					#crear nuevo analisis en bd
					insertar_analisis(id, pk, texto)
					flash('Enviado', 'success')
					response = make_response(redirect(url_for('details', name=name, pk=pk)))
				else :
					flash('Demasiado largo', 'danger')
					response = make_response(redirect(url_for('details', name=name, pk=get_videogame_id(name))))
		else :
			flash('Login requerido', 'danger')
			response = make_response(redirect(url_for('details', name=name, pk=get_videogame_id(name))))
		return response

def puntnMedia(pk):
    '''
    Parámetros: id de un videojuego
    Descripción: Recupera la puntuacion media
    Función: retorna un entero de la puntuación
    '''
    vid = Videojuego.query.filter_by(id=pk).first()
    return vid.puntnMedia
	
@app.route('/<name>/<int:select>/<int:noselect>/', methods=['POST'])
def jug_des(name, select, noselect):
		if 'nick' in session:
			id = get_user_id()
			jugado_deseado(id, get_videogame_id(name), select)
			flash('Enviado', 'success')
		else :
			flash('Login requerido', 'danger')
		response = make_response(redirect(url_for('details', name=name, pk=get_videogame_id(name))))
		return response

