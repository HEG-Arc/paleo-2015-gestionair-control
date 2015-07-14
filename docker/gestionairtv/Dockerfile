FROM digitallyseamless/nodejs-bower-grunt
WORKDIR /data
RUN git clone https://github.com/HEG-Arc/paleo-2015-gestionair-tv.git
WORKDIR /data/paleo-2015-gestionair-tv
RUN npm install
RUN bower install --allow-root
RUN grunt build
VOLUME ["/data/paleo-2015-gestionair-tv/dist"]