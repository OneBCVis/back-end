create table if not exists block
(
    block_hash          varchar(128)    not null,
    previous_block_hash varchar(128)    not null,
    height              int             not null,
    nonce               int             not null,
    difficulty          int             not null,
    miner               varchar(128),
    time_stamp          varchar(32)     not null,
    total_amount        int             not null,
    total_fee           int             not null,
    txn_count           int             not null,
    insert_time         bigint          not null
                default (unix_timestamp(current_timestamp(3)) * 1000),
    primary key (block_hash)
);

create table if not exists uncle
(
    uncle_hash          varchar(128)    not null,
    block_hash          varchar(128)    not null,
    primary key (uncle_hash),
    foreign key (block_hash) references block(block_hash)
        on delete cascade
);

create table if not exists off_chain_data
(
    block_hash          varchar(128)    not null,
    id                  varchar(128)    not null,
    txn_id              varchar(128),
    size                int             not null,
    primary key (block_hash, id),
    foreign key (block_hash) references block(block_hash)
        on delete cascade
);

create table if not exists txn_type
(
    type       int         not null,
    name       varchar(32) not null,
    primary key (type)
);

create table if not exists transaction
(
    txn_hash    varchar(128)                            not null,
    status      enum('PENDING', 'APPROVED', 'REJECTED') not null default 'PENDING',
    amount      int                                     not null,
    type        int                                     not null,
    nonce       int                                     not null,
    fee         int                                     not null,
    insert_time bigint                                  not null
                default (unix_timestamp(current_timestamp(3)) * 1000),
    primary key (txn_hash),
    foreign key (type) references txn_type(type)
);

create table if not exists txn_sender
(
    txn_hash    varchar(128) not null,
    sender_key  varchar(128) not null,
    amount      int          not null,
    primary key (txn_hash, sender_key),
    foreign key (txn_hash) references transaction(txn_hash)
        on delete cascade
);

create table if not exists txn_receiver
(
    txn_hash        varchar(128) not null,
    receiver_key    varchar(128) not null,
    amount          int          not null,
    primary key (txn_hash, receiver_key),
    foreign key (txn_hash) references transaction(txn_hash)
        on delete cascade
);

create table if not exists block_txn
(
    block_hash  varchar(128) not null,
    txn_hash    varchar(128) not null,
    primary key (txn_hash),
    foreign key (block_hash) references block(block_hash)
        on delete cascade,
    foreign key (txn_hash) references transaction(txn_hash)
        on delete cascade
);

create procedure insert_transaction(
    in t_hash varchar(128),
    in t_status enum('PENDING', 'APPROVED', 'REJECTED'),
    in t_amount int,
    in t_type int,
    in t_nonce int,
    in t_fee int,
    in t_senders json,
    in t_receivers json,
    in is_full boolean,
    out result int
)
ist: begin
    declare i int default 0;
    declare sender varchar(128);
    declare receiver varchar(128);
    declare amt int;

    if (select count(*) from transaction where txn_hash = t_hash) = 0 then
        insert into transaction (txn_hash, status, amount, type, nonce, fee)
            values (t_hash, t_status, t_amount, t_type, t_nonce, t_fee);

        set i = 0;
        while i < json_length(t_senders) do
            set sender = json_extract(json_extract(t_senders, concat('$[', i, ']')), '$[0]');
            set amt = json_extract(json_extract(t_senders, concat('$[', i, ']')), '$[1]');
            insert into txn_sender (txn_hash, sender_key, amount) values (t_hash, json_unquote(sender), amt);
            set i = i + 1;
        end while;

        set i = 0;
        while i < json_length(t_receivers) do
            set receiver = json_extract(json_extract(t_receivers, concat('$[', i, ']')), '$[0]');
            set amt = json_extract(json_extract(t_receivers, concat('$[', i, ']')), '$[1]');
            insert into txn_receiver (txn_hash, receiver_key, amount) values (t_hash, json_unquote(receiver), amt);
            set i = i + 1;
        end while;

        set result = 0;
        leave ist;
    else
        if is_full then
            update transaction
                set
                    status = t_status,
                    fee = t_fee
                where txn_hash = t_hash;
            set result = 1;
            leave ist;
        else
            set result = 2;
            leave ist;
        end if;
    end if;
    set result = -1;
    leave ist;
end;

create procedure insert_block_transactions(
    in ibt_b_hash varchar(128),
    in ibt_txns json,
    out ibt_result int
)
ibt: begin
    declare ibt_i int default 0;
    declare ibt_txn json;
    declare ibt_t_hash varchar(128);
    declare ibt_t_status varchar(16);
    declare ibt_t_amount int;
    declare ibt_t_type int;
    declare ibt_t_nonce int;
    declare ibt_t_fee int;
    declare ibt_t_senders json;
    declare ibt_t_receivers json;
    declare ibt_t_result int;
    declare ibt_total_amount int;
    declare ibt_total_fee int;

    set ibt_total_amount = 0;
    set ibt_total_fee = 0;
    set ibt_i = 0;
    while ibt_i < json_length(ibt_txns) do
        set ibt_txn = json_extract(ibt_txns, concat('$[', ibt_i, ']'));
        set ibt_t_hash = json_extract(ibt_txn, '$.Hash');
        set ibt_t_status = json_extract(ibt_txn, '$.Status');
        set ibt_t_amount = json_extract(ibt_txn, '$.Amount');
        set ibt_t_type = json_extract(ibt_txn, '$.Type');
        set ibt_t_nonce = json_extract(ibt_txn, '$.Nonce');
        set ibt_t_fee = json_extract(ibt_txn, '$.Fee');
        set ibt_t_senders = json_extract(ibt_txn, '$.Senders');
        set ibt_t_receivers = json_extract(ibt_txn, '$.Receivers');

        set ibt_total_amount = ibt_total_amount + ibt_t_amount;
        set ibt_total_fee = ibt_total_fee + ibt_t_fee;

        call insert_transaction(
            json_unquote(ibt_t_hash),
            json_unquote(ibt_t_status),
            ibt_t_amount,
            ibt_t_type,
            ibt_t_nonce,
            ibt_t_fee,
            ibt_t_senders,
            ibt_t_receivers,
            true,
            @ibt_t_result
        );

        insert into block_txn (block_hash, txn_hash) values (ibt_b_hash, json_unquote(ibt_t_hash));
        set ibt_i = ibt_i + 1;
    end while;
    update block
        set
            total_amount = ibt_total_amount,
            total_fee = ibt_total_fee,
            txn_count = json_length(ibt_txns)
        where block_hash = ibt_b_hash;
    set ibt_result = 0;
    leave ibt;
end;

create procedure insert_block_uncles(
    in ibu_b_hash varchar(128),
    in ibu_uncle_hashes json,
    out ibu_result int
)
ibu: begin
    declare ibu_i int default 0;
    declare ibu_u_hash varchar(128);

    set ibu_i = 0;
    while ibu_i < json_length(ibu_uncle_hashes) do
        set ibu_u_hash = lower(json_extract(ibu_uncle_hashes, concat('$[', ibu_i, ']')));
        insert into uncle (uncle_hash, block_hash) values (json_unquote(ibu_u_hash), ibu_b_hash);
        set ibu_i = ibu_i + 1;
    end while;
    set ibu_result = 0;
    leave ibu;
end;

create procedure insert_block_sidecar(
    in ibs_b_hash varchar(128),
    in ibs_sidecar json,
    out ibs_result int
)
ibs: begin
    declare ibs_i int default 0;
    declare ibs_ocd_id varchar(128);
    declare ibs_t_id varchar(128);
    declare ibs_ocd_size int;

    set ibs_i = 0;
    while ibs_i < json_length(ibs_sidecar) do
        set ibs_ocd_id = json_extract(json_extract(ibs_sidecar, concat('$[', ibs_i, ']')), '$.ID');
        set ibs_t_id = json_extract(json_extract(ibs_sidecar, concat('$[', ibs_i, ']')), '$.TransactionID');
        set ibs_ocd_size = json_extract(json_extract(ibs_sidecar, concat('$[', ibs_i, ']')), '$.Size');
        insert into off_chain_data (block_hash, id, txn_id, size) values (
            ibs_b_hash, json_unquote(ibs_ocd_id), json_unquote(ibs_t_id), ibs_ocd_size);
        set ibs_i = ibs_i + 1;
    end while;
    set ibs_result = 0;
    leave ibs;
end;
