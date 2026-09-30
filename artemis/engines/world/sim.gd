extends SceneTree
# Native Godot physics owns truth. Only sense() is passed to participant/model.
var server := TCPServer.new()
var clients := []
var buffers := {}
var secret := ""
var world: Node3D
var actor: CharacterBody3D
var objects := []
var tick := 0
var episode_seed := 17
var running := false
var pending_steps := 0
var waiting := []
var movement := Vector2.ZERO
var gaze := 0.0
var trace := []

func _initialize():
    var port := 19341
    for arg in OS.get_cmdline_user_args():
        if arg.begins_with("--port="): port = int(arg.trim_prefix("--port="))
        if arg.begins_with("--key="): secret = arg.trim_prefix("--key=")
    world = Node3D.new()
    root.add_child(world)
    reset(17)
    var code := server.listen(port, "127.0.0.1")
    if code != OK:
        print("ARTEMIS_ERROR: cannot bind World worker")
        quit(2)
    print("ARTEMIS_WORLD_READY " + str(port))

func box(name_: String, pos: Vector3, size: Vector3, color: String):
    var node := StaticBody3D.new()
    node.name = name_
    node.position = pos
    var collision := CollisionShape3D.new()
    var shape := BoxShape3D.new()
    shape.size = size
    collision.shape = shape
    node.add_child(collision)
    world.add_child(node)
    objects.append({"node":node,"name":name_,"position":pos,"size":size,"color":color})

func reset(seed_: int):
    running = false
    pending_steps = 0
    movement = Vector2.ZERO
    gaze = 0.0
    tick = 0
    trace.clear()
    for child in world.get_children():
        world.remove_child(child)
        child.free()
    objects.clear()
    episode_seed = seed_
    var rng := RandomNumberGenerator.new()
    rng.seed = seed_
    box("floor", Vector3(0,-0.25,0), Vector3(24,0.5,24), "#ccd1b9")
    box("occluder", Vector3(0,1,-1), Vector3(2,2,0.6), "#729487")
    box("block", Vector3(-3,0.6,-3), Vector3(1.2,1.2,1.2), "#d4b574")
    box("target", Vector3(rng.randf_range(2.5,4.5),0.5,-4), Vector3(1,1,1), "#819db3")
    actor = CharacterBody3D.new()
    actor.name = "body"
    actor.position = Vector3(0,1,4)
    var collision := CollisionShape3D.new()
    var shape := CapsuleShape3D.new()
    shape.radius = 0.3
    shape.height = 1.7
    collision.shape = shape
    actor.add_child(collision)
    world.add_child(actor)

func vec(v: Vector3): return [snappedf(v.x,0.00001),snappedf(v.y,0.00001),snappedf(v.z,0.00001)]

func sense():
    var visible := []
    var eye := actor.global_position + Vector3(0,0.6,0)
    var forward := Vector3.FORWARD.rotated(Vector3.UP,gaze)
    for item in objects:
        if item.name == "floor": continue
        var offset: Vector3 = item.node.global_position - eye
        var distance := offset.length()
        if distance > 8.0: continue
        var flat := Vector3(offset.x,0,offset.z).normalized()
        var angle := acos(clampf(forward.dot(flat),-1,1))
        if angle > deg_to_rad(40): continue
        var query := PhysicsRayQueryParameters3D.create(eye,item.node.global_position)
        query.exclude = [actor.get_rid()]
        var hit := world.get_world_3d().direct_space_state.intersect_ray(query)
        if hit.is_empty() or hit.collider != item.node: continue
        var bearing := atan2(forward.cross(flat).y,forward.dot(flat))
        visible.append({"label":item.name,"range_m":snappedf(distance,0.1),"bearing_rad":snappedf(bearing,0.01),"color":item.color})
    return {"tick":tick,"time_s":tick/60.0,"vision":{"fov_deg":80,"range_m":8,"objects":visible},"proprioception":{"position":vec(actor.position),"velocity":vec(actor.velocity),"gaze_yaw":gaze,"grounded":actor.is_on_floor()},"touch":{"contact":actor.get_slide_collision_count()>0},"quality":"native_physics_partial_sensor_frame"}

func truth():
    var items := []
    for item in objects:
        items.append({"name":item.name,"position":vec(item.node.global_position),"size":vec(item.size),"color":item.color})
    return {"tick":tick,"seed":episode_seed,"body":{"position":vec(actor.position),"velocity":vec(actor.velocity),"yaw":gaze},"objects":items,"running":running,"engine":"Godot 4 native physics","physics_hz":60}

func send(c, id_, data):
    c.put_data((JSON.stringify({"id":id_,"data":data})+"\n").to_utf8_buffer())

func command(c, m):
    if m.get("key", "") != secret:
        send(c,m.get("id",0),{"error":"Unauthorized native worker request"})
        return
    var id_ = m.get("id",0)
    match m.get("command", ""):
        "reset":
            reset(int(m.get("seed",17)))
            send(c,id_,truth())
        "sense": send(c,id_,sense())
        "truth": send(c,id_,truth())
        "play":
            running = bool(m.get("running",false))
            send(c,id_,truth())
        "intent":
            var x := clampf(float(m.get("move_x",0)),-1,1)
            var z := clampf(float(m.get("move_z",0)),-1,1)
            movement = Vector2(x,z).limit_length(1)
            gaze = wrapf(gaze+clampf(float(m.get("look_delta",0)),-0.5,0.5),-PI,PI)
            trace.append({"tick":tick,"move_x":x,"move_z":z,"look_delta":m.get("look_delta",0)})
            if trace.size()>4096: trace.pop_front()
            send(c,id_,{"accepted":true,"tick":tick,"intent_applied_by_controller":true})
        "advance":
            if running:
                send(c,id_,{"error":"Pause the independent clock before manual advance"})
            else:
                pending_steps += clampi(int(m.get("frames",1)),1,600)
                waiting.append({"client":c,"id":id_,"tick":tick+pending_steps})
        "trace": send(c,id_,trace)
        _: send(c,id_,{"error":"Unknown native command"})

func _process(_delta):
    while server.is_connection_available():
        var c := server.take_connection()
        clients.append(c)
        buffers[c] = ""
    for c in clients.duplicate():
        c.poll()
        if c.get_status()!=StreamPeerTCP.STATUS_CONNECTED:
            clients.erase(c)
            buffers.erase(c)
            continue
        if c.get_available_bytes()>0:
            var data = c.get_data(c.get_available_bytes())
            buffers[c] += data[1].get_string_from_utf8()
            if buffers[c].length()>65536:
                c.disconnect_from_host()
                continue
            while buffers[c].contains("\n"):
                var split = buffers[c].split("\n",true,1)
                buffers[c] = split[1]
                var m = JSON.parse_string(split[0])
                if m is Dictionary: command(c,m)
    return false

func _physics_process(delta):
    if running or pending_steps>0:
        var desired := Vector3(movement.x,0,-movement.y).rotated(Vector3.UP,gaze)*3.0
        actor.velocity.x = move_toward(actor.velocity.x,desired.x,8.0*delta)
        actor.velocity.z = move_toward(actor.velocity.z,desired.z,8.0*delta)
        if not actor.is_on_floor(): actor.velocity.y -= 9.8*delta
        actor.move_and_slide()
        tick += 1
        if pending_steps>0: pending_steps -= 1
    for item in waiting.duplicate():
        if tick>=item.tick:
            send(item.client,item.id,sense())
            waiting.erase(item)
    return false
