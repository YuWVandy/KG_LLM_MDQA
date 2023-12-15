import os

from parse import parse_args
from dataset import load_dataset
from learn import train, eval
from utils import seed_everything, load_saved
from loader import Dataset_process, Dataset_collate, Dataset_process2
from torch.utils.data import DataLoader
import math
import torch
from torch.optim import Adam
from transformers import (AutoConfig, AutoTokenizer,
                          get_linear_schedule_with_warmup)

from model import Retriever

def run(train_data, val_data, chunk_pool, model, tokenizer, collate, args):
    if args.do_train:
        no_decay = ['bias', 'LayerNorm.weight']
        optimizer_parameters = [
            {'params': [p for n, p in model.named_parameters() if not any(
                nd in n for nd in no_decay)], 'weight_decay': args.weight_decay},
            {'params': [p for n, p in model.named_parameters() if any(
                nd in n for nd in no_decay)], 'weight_decay': 0.0}
        ]
        optimizer = Adam(optimizer_parameters, lr = args.lr, eps = args.adam_epsilon)
        
        if args.dataset == 'HotpotQA':
            train_dataset = Dataset_process(train_data, tokenizer, args, train = True)
        else:
            train_dataset = Dataset_process2(train_data, chunk_pool, tokenizer, args, train = True)
        train_dataloader = DataLoader(train_dataset, batch_size = args.train_bsz, pin_memory = True, collate_fn = collate, num_workers = args.num_workers, shuffle=True)

        if args.dataset == 'HotpotQA':
            val_dataset = Dataset_process(val_data, tokenizer, args, train = False)
        else:
            val_dataset = Dataset_process2(val_data, chunk_pool, tokenizer, args, train = False)
        val_dataloader = DataLoader(val_dataset, batch_size = args.eval_bsz, pin_memory = True, collate_fn = collate, num_workers = args.num_workers, shuffle=False)
        
        t_total = len(train_dataloader) * args.epochs
        warmup_steps = math.ceil(t_total * args.warm_ratio)
        scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=warmup_steps, num_training_steps=t_total)
        best_mrr = 0

        for epoch in range(args.epochs):
            loss = train(model, train_dataloader, optimizer, scheduler, args)

            mrr = eval(model, val_dataloader)

            if mrr > best_mrr:
                best_mrr = mrr
                torch.save(model.state_dict(), './model/{}/model.pt'.format(args.dataset))

                print("Epoch: {}, Loss: {}, MRR: {}".format(epoch, loss, mrr))
                  
    else:
        val_dataset = Dataset_process(val_data, tokenizer, args, train = False)
        val_dataloader = DataLoader(val_dataset, batch_size = args.eval_bsz, pin_memory = True, collate_fn = collate, num_workers = args.num_workers, shuffle=False)
        
        mrr = eval(model, val_dataloader)

        print("MRR: {}".format(mrr))
                

if __name__ == "__main__":
    args = parse_args()
    args.path = os.getcwd()

    args.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    n_gpu = torch.cuda.device_count()

    seed_everything(args.seed)
    train_data, val_data, chunk_pool = load_dataset(args.dataset) 

    tokenizer = AutoTokenizer.from_pretrained(args.model_name)
    bert_config = AutoConfig.from_pretrained(args.model_name)

    model = Retriever(bert_config, args)

    if not args.do_train:
        model = load_saved(model, './model/{}/model.pt'.format(args.dataset), exact=False)

    model.to(args.device)
    model = torch.nn.DataParallel(model)

    run(train_data, val_data, chunk_pool, model, tokenizer, Dataset_collate, args)
