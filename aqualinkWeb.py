#!/usr/bin/python
# coding=utf-8

#import cherrypy
from webFrame import *
from htmlUtils import *

class WebUI(object):
    # constructor
    def __init__(self, theName, theContext, thePool):
        self.name = theName
        self.context = theContext
        self.pool = thePool

        if self.context.debug: self.context.log(self.name, "starting web thread")
#        globalConfig = {
#            'server.socket_port': 80,
#            'server.socket_host': "0.0.0.0",
#            }
#        appConfig = {
#            '/': {
#                'tools.staticdir.root': "/root"},
#            '/css': {
#                'tools.staticdir.on': True,
#                'tools.staticdir.dir': "css"},
#            '/favicon.ico': {
#                'tools.staticfile.on': True,
#                'tools.staticfile.filename': "/root/favicon.ico"},
#            }    
#        cherrypy.config.update(globalConfig)
#        root = WebRoot(self.name, self.context, self.pool)
#        cherrypy.tree.mount(root, "/", appConfig)
#        cherrypy.tree.mount(root.statusPage, "/status", appConfig)
#        cherrypy.tree.mount(root.poolPage, "/pool", appConfig)
#        cherrypy.engine.start()
#        self.context.log(self.name, "ready")
#        cherrypy.engine.block()
        root = WebRoot(self.name, self.context, self.pool)
        resources = {"/": root.index,
                     "/pool": root.poolPage,
                     "/status": root.statusPage,
                     "/favicon.ico": root.faviconPage,
                     "/css/phone.css": root.cssPage,
                     }
        webFrame = WebFrame("WebFrame", theContext, resources)
        webFrame.start()
        self.context.log(self.name, "ready")
        webFrame.block()
        if self.context.debug: self.context.log(self.name, "terminating web thread")

class WebRoot(object):

    # constructor
    def __init__(self, theName, theContext, thePool):
        self.name = theName
        self.context = theContext
        self.pool = thePool

        # mode dispatch table
        self.modeTable = {"Lights": WebRoot.lightsMode,
                          "Spa": WebRoot.spaMode,
                          "Clean": WebRoot.cleanMode,
                          }    

    def index(self):
        return self.poolPage()
    index.exposed = True

    def statusPage(self):
        if self.context.debugHttp: self.context.log(self.name, "statusPage")
        html = htmlDocument(htmlBody(htmlParagraph(self.pool.printState(end=htmlBreak())), 
                            [self.pool.title]), css="/css/phone.css", script=refreshScript(30))
        return html, "text/html; charset=UTF-8"
    statusPage.exposed = True

    def poolPage(self, mode=None):
        if self.context.debugHttp: self.context.log(self.name, "poolPage")
        if mode != None:
            self.modeTable[mode](self)
        html = htmlDocument(htmlBody(self.poolPageForm(), 
                            [self.pool.title]), css="/css/phone.css", script=refreshScript(10))
        return html, "text/html; charset=UTF-8"
    poolPage.exposed = True

    def poolPageForm(self):
        airTemp = "%3d"%self.pool.airTemp
        airColor = "white"
        poolTemp = "%3d"%self.pool.poolTemp
        poolColor = "aqua"
        if self.pool.spa.state:
            spaTemp = "%3d"%self.pool.spaTemp                      
            if self.pool.heater.state == "ON":
                spaColor = "red"
            else:
                spaColor = "green"
        else:
            spaTemp = "OFF"
            spaColor = "off"
        if self.pool.aux4.state or self.pool.aux5.state:
            lightsState = "ON"
            lightsColor = "lights"
        else:
            lightsState = "OFF"
            lightsColor = "off"
        html = htmlForm(htmlTable([[htmlDiv("label", "Air"), htmlDiv(airColor, airTemp)],
                          [htmlDiv("label", "Pool"), htmlDiv(poolColor, poolTemp)],
                          [htmlInput("", "submit", "mode", "Spa", theClass="button"), htmlDiv(spaColor, spaTemp)], 
                          [htmlInput("", "submit", "mode", "Lights", theClass="button"), htmlDiv(lightsColor, lightsState)]], 
                          [], [540, 460]), "mode", "pool")
        return html

    def lightsMode(self):
        if self.context.debugHttp: self.context.log(self.name, "lightsMode")
        self.pool.lightsMode.changeState()

    def spaMode(self):
        if self.context.debugHttp: self.context.log(self.name, "spaMode")
        self.pool.spaMode.changeState()

    def cleanMode(self):
        if self.context.debugHttp: self.context.log(self.name, "cleanMode")
        self.pool.cleanMode.changeState()

    def faviconPage(self):
        if self.context.debugHttp: self.context.log(self.name, "faviconPage")
        return self.readFile("favicon.ico"), "image/x-icon"

    def cssPage(self):
        if self.context.debugHttp: self.context.log(self.name, "cssPage")
        return self.readFile("css/phone.css"), "text/html; charset=UTF-8"
        
    def readFile(self, path):
        path = path.lstrip("/")
        if self.context.debugHttp: self.context.log(self.name, "reading", path)
        f = open(path)
        body = f.read()
        f.close()
        return body
    
