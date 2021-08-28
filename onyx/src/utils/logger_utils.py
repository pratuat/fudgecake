import os
import logging
import logging.handlers
from socket_log_receiver.receivers import serve, configure_logging

def get_logger(root_dir=None, filename='app.log', name='root', **kargs):

	basic_config_params = {
		'format' : '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
		**kargs,
		'level' : logging.DEBUG
	}

	if not kargs.get('handlers') or not kargs.get('stream'):
		if not root_dir or not os.path.exists(root_dir):
			root_dir = os.getcwd()

		log_dir = os.path.join(root_dir, 'logs')

		if not os.path.exists(log_dir):
			os.mkdir(log_dir)

		basic_config_params['filename'] = os.path.join(log_dir, filename)

	logging.basicConfig(**basic_config_params)
	logger = logging.getLogger(name)
	logger.setLevel(kargs.get('level', logging.DEBUG))

	return logger

def get_socket_logger(host='127.0.0.1', port=9020, name='root', level='DEBUG'):
	handler = logging.handlers.SocketHandler(host=host, port=port)
	logger = logging.getLogger(name)
	logger.addHandler(handler)
	logger.setLevel(level)

	return logger

def start_logging_server(
	root_dir=None,
	filename='cbas.log',
	filemode='+a',
	level='INFO',
	host='127.0.0.1',
	port=9020,
	format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
	datefmt="%Y-%m-%d %H:%M:%S",
	**kargs):

	if not root_dir or not os.path.exists(root_dir):
		root_dir = os.getcwd()

	log_dir = os.path.join(root_dir, 'logs')

	if not os.path.exists(log_dir):
		os.mkdir(log_dir)

	filepath = os.path.join(log_dir, filename)

	config = {
		'host' : host,
		'port' : port,
		'level' : level,
		'filename' : filepath,
		'filemode' : filemode,
		'format' : format,
		'datefmt' : datefmt
	}

	configure_logging(None, None, config)
	serve(None, None, config)
