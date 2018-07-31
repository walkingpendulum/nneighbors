# nneighbors

Find'n'add nearest neighbors!

# Requirements
* docker-compose

# Getting started
For running application:
```
$ bash setup.sh
```

Add someone:
```
$ curl -XPOST http://$(docker-machine ip):8888/add -d '{"name": "walkingpendulum", "coordinates": [0, 0]}'
```

Find nearest:
```
$ curl -XPOST http://$(docker-machine ip):8888/near -d '{"coordinates": [0, 0]}'
```
