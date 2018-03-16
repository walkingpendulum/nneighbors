# nneighborhood

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
$ host=$(echo $(docker-machine ip)) curl -XPOST http://$host:8888/add -d '{"name": "walkingpendulum", "coordinates": [0, 0]}'
```

Find nearest:
```
$ host=$(echo $(docker-machine ip)) curl -XPOST http://$host:8888/near -d '{"coordinates": [0, 0]}'
```
