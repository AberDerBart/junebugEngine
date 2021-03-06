import json
import pygame
import os.path
from .util import relativePath
from .parsers import parseProperties


class Tile:
    def __init__(self, surf, data):
        self.surf = surf

        self.properties = {}

        for prop in data['properties']:
            if prop['name'] in ['collide', 'collision']:
                self.collide = prop['value']
            self.properties[prop["name"]] = prop["value"]

    def getSurf(self):
        if self.properties.get("invisible"):
            return None
        return self.surf

    def collides(self):
        return self.collide


class SetDict:
    def __init__(self, data, relFile):
        self.sets = {}
        for tileset in data:
            path = relativePath(tileset['source'], relFile)
            data = json.load(open(path))

            # TODO: pathname is checked for legacy entitysets, remove this
            if "image" in data and not os.path.basename(path).startswith('entities'):
                tmpSet = TileSet.get(path)
                firstGid = tileset["firstgid"]
                lastGid = firstGid + tmpSet.length()
                self.sets[range(firstGid, lastGid)] = tmpSet
            else:
                tmpSet = EntitySet.get(path)
                firstGid = tileset["firstgid"]
                lastGid = firstGid + tmpSet.maxId()
                self.sets[range(firstGid, lastGid + 1)] = tmpSet

    def get(self, index):
        for indexRange in self.sets.keys():
            if index in indexRange:
                return self.sets[indexRange].getObj(index - indexRange.start)


class EntityData:
    generators = {}

    @staticmethod
    def getType(entityType):
        return EntityData.generators.get(entityType)

    @staticmethod
    def registerType(entityType):
        typeName = entityType.__dict__.get("typeName") or entityType.__class__.__name__
        print("Registering type", typeName)
        EntityData.generators[typeName] = entityType

    def getGenerator(self):
        return EntityData.generators.get(self.entityType)

    def __init__(self, data, relPath):
        self.path = relPath
        self.entityType = None
        self.properties = {}
        self.entityType = data.get('type')
        self.properties = parseProperties(data.get('properties', []), relPath)

class EntitySet:
    sets = {}

    @staticmethod
    def get(path):
        """returns the EntitySet specified by path, loading it if necessary"""

        path = os.path.abspath(path)
        if path in EntitySet.sets:
            print("EntitySet already loaded:", path)
            return EntitySet.sets[path]

        print("Loading EntitySet:", path)

        es = EntitySet()

        data = json.load(open(path))

        entityData = data["tiles"]

        es.entities = {}

        for entity in entityData:
            entityId = entity['id']
            es.entities[entityId] = EntityData(entity, path)

        EntitySet.sets[path] = es
        return es

    def maxId(self):
        return max(self.entities.keys())

    def getObj(self, index):
        return self.entities.get(index)


class TileSet:
    sets = {}

    @staticmethod
    def get(path):
        """returns the tileset specified by path, loading it if necessary"""

        absPath = os.path.abspath(path)
        if absPath in TileSet.sets:
            print('Tileset already loaded:', absPath)
            return TileSet.sets[absPath]

        print('Loading Tileset:', absPath)

        ts = TileSet()

        data = json.load(open(absPath))

        transparent = data['transparentcolor']
        tileWidth = data['tilewidth']
        tileHeight = data['tileheight']

        imageRelPath = data['image']
        dirname = os.path.dirname(absPath)
        imageAbsPath = os.path.join(dirname, imageRelPath)

        image = pygame.image.load(imageAbsPath).convert()
        image.set_colorkey(pygame.Color(transparent))

        columns = data['columns']
        ts.tiles = []

        for index, tile in enumerate(data['tiles']):
            column = index % columns
            row = int(index / columns)
            rect = pygame.Rect(column * tileWidth,
                               row * tileHeight,
                               tileWidth,
                               tileHeight)

            surf = image.subsurface(rect)
            surf = pygame.transform.scale(surf,
                                          (int(tileWidth),
                                           int(tileHeight)))

            ts.tiles.append(Tile(surf, tile))

        TileSet.sets[absPath] = ts
        return ts

    def length(self):
        return len(self.tiles)

    def getObj(self, index):
        return self.tiles[index]
