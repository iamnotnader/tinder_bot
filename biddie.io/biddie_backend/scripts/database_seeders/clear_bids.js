use server;
db.bids.remove({receiver_id: ObjectId('54b7385d194498a1acecc5c1')});
db.bids.remove({sender_id: ObjectId('54b7385d194498a1acecc5c1')});
db.pokes.remove({receiver_id: ObjectId('54b7385d194498a1acecc5c1')});
db.pokes.remove({sender_id: ObjectId('54b7385d194498a1acecc5c1')});

db.bids.remove({sender_id: ObjectId('54c53ed54298651ae2758044')});
db.bids.remove({receiver_id: ObjectId('54c53ed54298651ae2758044')});
db.pokes.remove({receiver_id: ObjectId('54c53ed54298651ae2758044')});
db.pokes.remove({sender_id: ObjectId('54c53ed54298651ae2758044')});
